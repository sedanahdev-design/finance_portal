from decimal import Decimal

from django.contrib import messages
from django.core.files.base import ContentFile
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render

from commissions.engine import (
    compute_company_breakdown, compute_rep_commissions, merge_additions,
    parse_additions, parse_movement, parse_rates, parse_sanitizer_targets,
)
from commissions.excel_export import build_workbook
from commissions.forms import CommissionUploadForm
from commissions.models import CommissionRun
from core.audit import log_action
from core.decorators import module_required
from core.models import AuditLog

PREVIEW_LIMIT = 60


@module_required("commissions")
def index(request):
    form = CommissionUploadForm()
    runs = CommissionRun.objects.select_related("created_by")[:15]
    return render(request, "commissions/index.html", {"form": form, "runs": runs})


@module_required("commissions", edit=True)
def run_view(request):
    if request.method != "POST":
        return redirect("commissions:index")
    form = CommissionUploadForm(request.POST, request.FILES)
    if not form.is_valid():
        runs = CommissionRun.objects.select_related("created_by")[:15]
        return render(request, "commissions/index.html", {"form": form, "runs": runs})

    d = form.cleaned_data
    try:
        rates = parse_rates(d["rates_file"])
        sales_rows = parse_movement(d["sales_file"])
        return_rows = parse_movement(d["returns_file"])
        sanitizer_targets = parse_sanitizer_targets(d["sanitizer_targets_file"]) if d.get("sanitizer_targets_file") else {}
        additions = parse_additions(d["additions_file"]) if d.get("additions_file") else None
    except Exception as exc:  # noqa: BLE001
        messages.error(request, f"تعذّرت قراءة أحد الملفات: {exc}")
        log_action(request, AuditLog.Action.ERROR, str(exc), module_code="commissions")
        return redirect("commissions:index")

    rep_commissions = compute_rep_commissions(sales_rows, rates, sanitizer_targets, return_rows=return_rows)
    company_breakdown = compute_company_breakdown(rep_commissions)

    total_sales = sum((v["total_sales"] for v in rep_commissions.values()), Decimal("0"))
    total_commission = sum((v["total_commission"] for v in rep_commissions.values()), Decimal("0"))
    unrated = set()
    for v in rep_commissions.values():
        unrated.update(v.get("unrated_companies", set()))

    summary = {
        "reps_count": len(rep_commissions), "total_sales": total_sales, "total_commission": total_commission,
        "unrated_companies_count": len(unrated),
    }

    # ميزة "ملف الإضافات" (2026-09-27، اختيارية) — انظر توثيق الصيغة في
    # commissions/engine.py (merge_additions).
    merged = merge_additions(rep_commissions, additions) if additions is not None else None
    additions_missing_count = additions_unmatched_count = 0
    total_due = total_commission
    total_net = total_commission
    if merged is not None:
        additions_missing_count = sum(1 for m in merged.values() if not m["has_addition_row"])
        additions_unmatched_count = sum(1 for m in merged.values() if not m["has_sales"])
        total_due = sum((m["due"] for m in merged.values()), Decimal("0"))
        total_net = sum((m["net"] for m in merged.values()), Decimal("0"))

    run = CommissionRun.objects.create(
        created_by=request.user, reps_count=summary["reps_count"],
        total_sales=total_sales, total_commission=total_commission,
        unrated_companies_count=summary["unrated_companies_count"],
        additions_used=merged is not None, total_due=total_due, total_net=total_net,
        additions_missing_count=additions_missing_count, additions_unmatched_count=additions_unmatched_count,
    )
    buf = build_workbook(rep_commissions, company_breakdown, summary, merged=merged)
    run.result_file.save(f"عمولات_{run.pk}.xlsx", ContentFile(buf.read()), save=True)

    log_action(request, AuditLog.Action.RUN, f"عمولات #{run.pk}", module_code="commissions", meta={"run_id": run.pk})
    if unrated:
        messages.warning(request, f"توجد {len(unrated)} شركة غير موجودة في جدول نسب العمولات، احتُسبت عمولتها صفراً — راجع شيت 'شركات بلا نسبة'.")
    else:
        messages.success(request, f"تم احتساب عمولات {summary['reps_count']} مندوب/كول سنتر بنجاح.")
    if merged is not None:
        messages.success(
            request,
            f"تم دمج ملف الإضافات — إجمالي المستحق {total_due:,.2f}، إجمالي الصافي (بعد خصم السلف) {total_net:,.2f}.",
        )
        if additions_missing_count:
            messages.info(
                request,
                f"{additions_missing_count} مندوب له عمولة محسوبة بلا صف مطابق بملف الإضافات (احتُسبت إضافاته صفراً) "
                f"— راجع شيت \"مندوبون بلا صف إضافات\".",
            )
        if additions_unmatched_count:
            messages.warning(
                request,
                f"{additions_unmatched_count} اسم بملف الإضافات بلا مبيعات مطابقة هذا الشهر — راجع شيت "
                f"\"أسماء بملف الإضافات غير مطابقة\" (تحقق من خطأ إملائي محتمل بالاسم).",
            )

    preview = []
    for rep, data in sorted(rep_commissions.items())[:PREVIEW_LIMIT]:
        preview.append({
            "rep": rep, "sales": str(data["total_sales"]), "commission": str(data["total_commission"]),
        })
    request.session[f"comm_preview_{run.pk}"] = preview

    company_preview = []
    for company, c in sorted(company_breakdown.items(), key=lambda kv: kv[1]["commission"], reverse=True)[:PREVIEW_LIMIT]:
        company_preview.append({
            "company": company, "sales": str(c["sales"]), "commission": str(c["commission"]),
        })
    request.session[f"comm_company_preview_{run.pk}"] = company_preview
    return redirect("commissions:result", pk=run.pk)


@module_required("commissions")
def result(request, pk):
    run = get_object_or_404(CommissionRun, pk=pk)
    preview = request.session.get(f"comm_preview_{run.pk}", [])
    company_preview = request.session.get(f"comm_company_preview_{run.pk}", [])
    return render(request, "commissions/result.html", {"run": run, "preview": preview, "company_preview": company_preview})


@module_required("commissions")
def download(request, pk):
    run = get_object_or_404(CommissionRun, pk=pk)
    if not run.result_file:
        raise Http404
    log_action(request, AuditLog.Action.EXPORT, f"تنزيل عمولات #{run.pk}", module_code="commissions")
    return FileResponse(run.result_file.open("rb"), as_attachment=True, filename=f"عمولات_{run.pk}.xlsx")
