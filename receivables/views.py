from decimal import Decimal

from django.contrib import messages
from django.core.files.base import ContentFile
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render

from core.audit import log_action
from core.decorators import module_required
from core.models import AuditLog
from receivables.engine import parse_ledger, reconcile
from receivables.excel_export import build_workbook
from receivables.forms import ReceivablesUploadForm
from receivables.models import ReceivablesRun

PREVIEW_LIMIT = 60


@module_required("receivables")
def index(request):
    form = ReceivablesUploadForm()
    runs = ReceivablesRun.objects.select_related("created_by")[:15]
    return render(request, "receivables/index.html", {"form": form, "runs": runs})


@module_required("receivables", edit=True)
def run_view(request):
    if request.method != "POST":
        return redirect("receivables:index")
    form = ReceivablesUploadForm(request.POST, request.FILES)
    if not form.is_valid():
        runs = ReceivablesRun.objects.select_related("created_by")[:15]
        return render(request, "receivables/index.html", {"form": form, "runs": runs})

    f = form.cleaned_data["ledger_file"]
    try:
        rows = parse_ledger(f)
    except Exception as exc:  # noqa: BLE001
        messages.error(request, f"تعذّرت قراءة الملف: {exc}")
        log_action(request, AuditLog.Action.ERROR, str(exc), module_code="receivables")
        return redirect("receivables:index")

    if not rows:
        messages.error(request, "لم يتم العثور على أي حركات صالحة داخل الملف.")
        return redirect("receivables:index")

    result = reconcile(rows)
    s = result["summary"]

    run = ReceivablesRun.objects.create(
        created_by=request.user, source_file_name=f.name,
        total_rows=s["total_rows"], linked_rows=s["linked_rows"], unlinked_rows=s["unlinked_rows"],
        groups_count=s["groups_count"], matched_groups=s["matched_groups"], mismatched_groups=s["mismatched_groups"],
        mismatched_amount=Decimal(s["mismatched_amount"]),
    )
    buf = build_workbook(result, {"file_name": f.name})
    run.result_file.save(f"مطابقة_ذمم_{run.pk}.xlsx", ContentFile(buf.read()), save=True)

    log_action(request, AuditLog.Action.RUN, f"مطابقة ذمم #{run.pk}", module_code="receivables", meta={"run_id": run.pk})
    if s["mismatched_groups"]:
        messages.warning(request, f"توجد {s['mismatched_groups']} مجموعة غير متطابقة تحتاج مراجعة.")
    else:
        messages.success(request, "تمت المطابقة بنجاح، جميع أرقام البيان متطابقة.")

    def grp_json(g):
        return {
            "statement_numbers": g["statement_numbers"], "subaccounts": g["subaccounts"],
            "total_debit": str(g["total_debit"]), "total_credit": str(g["total_credit"]),
            "difference": str(g["difference"]), "matched": g["matched"], "rows_count": len(g["rows"]),
        }

    request.session[f"recv_preview_{run.pk}"] = {
        "mismatched": [grp_json(g) for g in result["mismatched_groups"][:PREVIEW_LIMIT]],
        "unlinked": [{"date": r["date"], "voucher_no": r["voucher_no"], "narration": r["narration"],
                       "debit": str(r["debit"]), "credit": str(r["credit"])} for r in result["unlinked"][:PREVIEW_LIMIT]],
    }
    return redirect("receivables:result", pk=run.pk)


@module_required("receivables")
def result(request, pk):
    run = get_object_or_404(ReceivablesRun, pk=pk)
    preview = request.session.get(f"recv_preview_{run.pk}", {"mismatched": [], "unlinked": []})
    return render(request, "receivables/result.html", {"run": run, "preview": preview})


@module_required("receivables")
def download(request, pk):
    run = get_object_or_404(ReceivablesRun, pk=pk)
    if not run.result_file:
        raise Http404
    log_action(request, AuditLog.Action.EXPORT, f"تنزيل مطابقة ذمم #{run.pk}", module_code="receivables")
    return FileResponse(run.result_file.open("rb"), as_attachment=True, filename=f"مطابقة_ذمم_{run.pk}.xlsx")
