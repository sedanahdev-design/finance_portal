from decimal import Decimal

from django.contrib import messages
from django.core.files.base import ContentFile
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render

from core.audit import log_action
from core.decorators import module_required
from core.models import AuditLog
from distributor_commissions.engine import (
    ROLE_ORDER,
    compute_collection_role_breakdown,
    compute_collection_situation_breakdown,
    compute_return_role_breakdown,
    compute_return_situation_breakdown,
    compute_totals,
    parse_distributor_file,
)
from distributor_commissions.excel_export import build_workbook
from distributor_commissions.forms import DistributorCommissionUploadForm
from distributor_commissions.models import DistributorCommissionRun

PREVIEW_LIMIT = 60


@module_required("distributor_commissions")
def index(request):
    form = DistributorCommissionUploadForm()
    runs = DistributorCommissionRun.objects.select_related("created_by")[:15]
    return render(request, "distributor_commissions/index.html", {"form": form, "runs": runs})


@module_required("distributor_commissions", edit=True)
def run_view(request):
    if request.method != "POST":
        return redirect("distributor_commissions:index")
    form = DistributorCommissionUploadForm(request.POST, request.FILES)
    if not form.is_valid():
        runs = DistributorCommissionRun.objects.select_related("created_by")[:15]
        return render(request, "distributor_commissions/index.html", {"form": form, "runs": runs})

    ledger_f = form.cleaned_data["ledger_file"]
    try:
        parsed = parse_distributor_file(ledger_f)
    except Exception as exc:  # noqa: BLE001
        messages.error(request, f"تعذّرت قراءة الملف: {exc}")
        log_action(request, AuditLog.Action.ERROR, str(exc), module_code="distributor_commissions")
        return redirect("distributor_commissions:index")

    result = compute_totals(parsed)
    situation_breakdown = compute_collection_situation_breakdown(parsed.collection_rows)
    return_situation_breakdown = compute_return_situation_breakdown(parsed.return_rows)
    role_breakdown = compute_collection_role_breakdown(parsed.collection_rows)
    return_role_breakdown = compute_return_role_breakdown(parsed.return_rows)

    total_debit = sum((r.debit for r in parsed.collection_rows), Decimal("0"))
    unresolved_rows_count = len(parsed.unresolved_collection_rows) + len(parsed.unresolved_return_rows)
    summary = {
        "rows_count": len(parsed.collection_rows),
        "return_rows_count": len(parsed.return_rows),
        "distributors_count": len(result["totals"]),
        "total_debit": total_debit,
        "collection_total": result["collection_total"],
        "return_total": result["return_total"],
        "total_commission": result["grand_total"],
    }

    run = DistributorCommissionRun.objects.create(
        created_by=request.user, ledger_file_name=ledger_f.name,
        distributors_count=summary["distributors_count"], rows_count=summary["rows_count"],
        return_rows_count=summary["return_rows_count"], total_debit=total_debit,
        total_commission=summary["total_commission"], collection_total=summary["collection_total"],
        return_total=summary["return_total"], flagged_rows_count=len(parsed.flagged_rows),
        warehouse_excluded_count=parsed.warehouse_excluded_count,
        fuzzy_biyad_rows_count=len(parsed.fuzzy_biyad_rows),
        unresolved_rows_count=unresolved_rows_count,
    )
    buf = build_workbook(
        parsed, result, summary, {"ledger_file_name": ledger_f.name},
        situation_breakdown=situation_breakdown,
        return_situation_breakdown=return_situation_breakdown,
        role_breakdown=role_breakdown,
        return_role_breakdown=return_role_breakdown,
    )
    run.result_file.save(f"عمولة_تحصيل_{run.pk}.xlsx", ContentFile(buf.read()), save=True)

    log_action(request, AuditLog.Action.RUN, f"عمولة تحصيل موزعين #{run.pk}",
               module_code="distributor_commissions", meta={"run_id": run.pk})
    if parsed.flagged_rows:
        messages.warning(
            request,
            f"تم الاحتساب لـ {summary['distributors_count']} موزع، "
            f"مع {len(parsed.flagged_rows)} حركة تحتاج مراجعة يدوية (راجع شيت 'حركات للمراجعة' في الملف).",
        )
    else:
        messages.success(request, f"تم احتساب عمولة تحصيل {summary['distributors_count']} موزع بنجاح.")
    if parsed.fuzzy_biyad_rows:
        messages.warning(
            request,
            f"{len(parsed.fuzzy_biyad_rows)} حركة فيها مشارك من نص البيان بمطابقة تقريبية فقط (لوّنت برتقالياً) "
            f"— راجع شيت 'مطابقة تقريبية من البيان' للتأكد يدوياً.",
        )
    if unresolved_rows_count:
        messages.error(
            request,
            f"{unresolved_rows_count} حركة بلا أي موزع معروف إطلاقاً (لوّنت أحمر، ولم تُحتسب لأي موزع) "
            f"— راجع شيت 'حركات بلا أي موزع معروف' واحتسبها يدوياً.",
        )

    preview = [
        {
            "name": name,
            "collection": str(result["collection_commission"].get(name, Decimal("0"))),
            "returns": str(result["return_commission"].get(name, Decimal("0"))),
            "commission": str(amount),
            # تفصيل الحالات (منفرد/مع شخص آخر/مجموعة) لعمولة التحصيل النقدي فقط —
            # لعرض مختصر قابل للطي في صفحة النتيجة؛ التفصيل الكامل (مع المرتجعات)
            # في شيت "تفصيل كل موزع حسب الحالة" بالملف المُصدَّر.
            "situations": [
                {
                    "label": sit,
                    "count": b["count"],
                    "amount": str(b["amount"]),
                    "commission": str(b["commission"]),
                }
                for sit, b in situation_breakdown.get(name, {}).items()
                if b["count"] > 0
            ],
            # تفصيل الأدوار/الحالات (سائق السيارة/مساعد/دراجة/.../من البيان) —
            # طلب المستخدم 2026-09-28: "توتال التحصيل لكل حالة ... ونسبة كل
            # حالة". التفصيل الكامل (مع المرتجعات) في شيت "تفصيل كل موزع حسب
            # الدور" بالملف المُصدَّر.
            "roles": [
                {
                    "label": role,
                    "count": b["count"],
                    "amount": str(b["amount"]),
                    "commission": str(b["commission"]),
                    "rate": f"{(b['commission'] / b['amount'] * 100):.3f}%" if b["amount"] else "—",
                }
                for role in ROLE_ORDER
                for b in [role_breakdown.get(name, {}).get(role)]
                if b and b["count"] > 0
            ],
        }
        for name, amount in sorted(result["totals"].items())
    ][:PREVIEW_LIMIT]
    request.session[f"distcomm_preview_{run.pk}"] = preview
    return redirect("distributor_commissions:result", pk=run.pk)


@module_required("distributor_commissions")
def result(request, pk):
    run = get_object_or_404(DistributorCommissionRun, pk=pk)
    preview = request.session.get(f"distcomm_preview_{run.pk}", [])
    return render(request, "distributor_commissions/result.html", {"run": run, "preview": preview})


@module_required("distributor_commissions")
def download(request, pk):
    run = get_object_or_404(DistributorCommissionRun, pk=pk)
    if not run.result_file:
        raise Http404
    log_action(request, AuditLog.Action.EXPORT, f"تنزيل عمولة تحصيل موزعين #{run.pk}",
               module_code="distributor_commissions")
    return FileResponse(run.result_file.open("rb"), as_attachment=True, filename=f"عمولة_تحصيل_{run.pk}.xlsx")
