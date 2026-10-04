from decimal import Decimal

from django.contrib import messages
from django.core.files.base import ContentFile
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render

from core.audit import log_action
from core.decorators import module_required
from core.models import AuditLog
from dawak_compare.engine import build_result, parse_dawak_project, parse_hiba_statement
from dawak_compare.excel_export import build_workbook
from dawak_compare.forms import DawakCompareUploadForm
from dawak_compare.models import DawakCompareRun


@module_required("dawak_compare")
def index(request):
    form = DawakCompareUploadForm()
    runs = DawakCompareRun.objects.select_related("created_by")[:15]
    return render(request, "dawak_compare/index.html", {"form": form, "runs": runs})


@module_required("dawak_compare", edit=True)
def run_view(request):
    if request.method != "POST":
        return redirect("dawak_compare:index")
    form = DawakCompareUploadForm(request.POST, request.FILES)
    if not form.is_valid():
        runs = DawakCompareRun.objects.select_related("created_by")[:15]
        return render(request, "dawak_compare/index.html", {"form": form, "runs": runs})

    dawak_f = form.cleaned_data["dawak_file"]
    hiba_f = form.cleaned_data["hiba_file"]
    try:
        pharmacies = parse_dawak_project(dawak_f)
        hiba_totals = parse_hiba_statement(hiba_f)
    except Exception as exc:  # noqa: BLE001
        messages.error(request, f"تعذّرت قراءة الملفات: {exc}")
        log_action(request, AuditLog.Action.ERROR, str(exc), module_code="dawak_compare")
        return redirect("dawak_compare:index")

    result = build_result(pharmacies, hiba_totals)
    s = result["summary"]
    payments = result.get("payments")
    ps = payments["summary"] if payments else {}
    cost_centers = result.get("cost_centers")
    ccs = cost_centers["summary"] if cost_centers else {}

    run = DawakCompareRun.objects.create(
        created_by=request.user, dawak_file_name=dawak_f.name, hiba_file_name=hiba_f.name,
        pharmacies_count=s["pharmacies_count"], matched_count=s["matched_count"],
        mismatched_count=s["mismatched_count"], mismatched_amount=Decimal(s["mismatched_amount"]),
        hiba_balance=Decimal(s["hiba_balance"]),
        payments_dawak_count=ps.get("dawak_entries_count", 0),
        payments_hiba_count=ps.get("hiba_entries_count", 0),
        payments_matched_count=ps.get("matched_count", 0),
        payments_found_diff_date_count=ps.get("found_diff_date_count", 0),
        payments_found_diff_date_amount=Decimal(str(ps.get("found_diff_date_amount", 0))),
        payments_true_diff_count=ps.get("true_diff_count", 0),
        payments_true_diff_amount=Decimal(str(ps.get("true_diff_amount", 0))),
        cc_matched_count=ccs.get("matched", 0),
        cc_mismatched_count=ccs.get("mismatched", 0),
        cc_no_hiba_data_count=ccs.get("no_hiba_data", 0),
        cc_unresolved_hiba_rows=ccs.get("unresolved_hiba_rows", 0),
    )
    buf = build_workbook(result, {"dawak_file_name": dawak_f.name, "hiba_file_name": hiba_f.name})
    run.result_file.save(f"مطابقة_دواك_{run.pk}.xlsx", ContentFile(buf.read()), save=True)

    log_action(request, AuditLog.Action.RUN, f"مطابقة دواك #{run.pk}", module_code="dawak_compare", meta={"run_id": run.pk})
    msgs = []
    if s["mismatched_count"]:
        msgs.append(f"توجد {s['mismatched_count']} صيدلية غير متطابقة (داخل ملف دواك وحده).")
    if ccs.get("mismatched"):
        msgs.append(
            f"توجد {ccs['mismatched']} صيدلية/حساب فرعي فرقه غير مطابق فعلياً مع هبة (حسب مركز الكلفة) — راجع شيت 'مطابقة حسب مركز الكلفة'.",
        )
    if ccs.get("unresolved_hiba_rows"):
        msgs.append(
            f"توجد {ccs['unresolved_hiba_rows']} حركة بملف هبة لها مركز كلفة لم نجد له أي صيدلية مطابقة بثقة بملف دواك — تحتاج مراجعة يدوية.",
        )
    if ps.get("found_diff_date_count"):
        msgs.append(
            f"تم العثور على {ps['found_diff_date_count']} دفعة بنفس المبلغ عند الطرف الآخر لكن بتاريخ مختلف "
            f"(إجمالي {ps['found_diff_date_amount']}) — راجع شيت 'موجود بتاريخ مختلف' في ملف النتيجة.",
        )
    if msgs:
        messages.warning(request, " ".join(msgs))
    else:
        messages.success(request, "جميع الصيدليات متطابقة (داخلياً ومع هبة)، ولم يتم العثور على أي فروقات في الدفعات.")

    request.session[f"dawak_preview_{run.pk}"] = [
        {"code": p["code"], "name": p["name"], "total_debit": str(p["total_debit"]),
         "total_credit": str(p["total_credit"]), "difference": str(p["difference"]), "matched": p["matched"]}
        for p in result["pharmacies"]
    ]

    STATUS_LABEL = {"matched": "مطابق مع هبة", "mismatched": "غير مطابق مع هبة", "no_hiba_data": "لا توجد حركات مقابلة عند هبة"}
    if cost_centers:
        request.session[f"dawak_cc_preview_{run.pk}"] = [
            {
                "code": r["code"], "name": r["name"], "status": STATUS_LABEL.get(r["status"], r["status"]),
                "dawak_debit": str(r["dawak_debit"]), "dawak_credit": str(r["dawak_credit"]),
                "hiba_debit": str(r["hiba_debit"]), "hiba_credit": str(r["hiba_credit"]),
                "hiba_rows_count": r["hiba_rows_count"],
                "diff_vs_hiba_debit": str(r["diff_vs_hiba_debit"]), "diff_vs_hiba_credit": str(r["diff_vs_hiba_credit"]),
            }
            for r in cost_centers["rows"]
        ]
        request.session[f"dawak_cc_unresolved_preview_{run.pk}"] = [
            {"cost_center": e.get("cost_center", ""), "narration": e.get("narration", ""),
             "debit": str(e.get("debit", 0)), "credit": str(e.get("credit", 0)),
             "raw_date": e.get("raw_date", "")}
            for e in cost_centers["unresolved"][:60]
        ]

    def _entry_date_str(e):
        d = e.get("entry_date")
        return d.isoformat() if d else (e.get("raw_date") or "")

    if payments:
        request.session[f"dawak_payments_preview_{run.pk}"] = [
            {
                "amount": str(p["amount"]),
                "dawak_side": f'{p["a"]["pharmacy_name"]} — {_entry_date_str(p["a"])}' if p.get("a") else "—",
                "hiba_side": _entry_date_str(p["b"]) if p.get("b") else "—",
                "note": p.get("note", ""),
            }
            for p in payments["found_diff_date"][:60]
        ]
    return redirect("dawak_compare:result", pk=run.pk)


@module_required("dawak_compare")
def result(request, pk):
    run = get_object_or_404(DawakCompareRun, pk=pk)
    preview = request.session.get(f"dawak_preview_{run.pk}", [])
    payments_preview = request.session.get(f"dawak_payments_preview_{run.pk}", [])
    cc_preview = request.session.get(f"dawak_cc_preview_{run.pk}", [])
    cc_unresolved_preview = request.session.get(f"dawak_cc_unresolved_preview_{run.pk}", [])
    return render(request, "dawak_compare/result.html", {
        "run": run, "preview": preview, "payments_preview": payments_preview,
        "cc_preview": cc_preview, "cc_unresolved_preview": cc_unresolved_preview,
    })


@module_required("dawak_compare")
def download(request, pk):
    run = get_object_or_404(DawakCompareRun, pk=pk)
    if not run.result_file:
        raise Http404
    log_action(request, AuditLog.Action.EXPORT, f"تنزيل مطابقة دواك #{run.pk}", module_code="dawak_compare")
    return FileResponse(run.result_file.open("rb"), as_attachment=True, filename=f"مطابقة_دواك_{run.pk}.xlsx")
