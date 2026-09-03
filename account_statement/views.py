from django.contrib import messages
from django.core.files.base import ContentFile
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render

from account_statement.engine import parse_statement, split_by_currency
from account_statement.excel_export import build_workbook
from account_statement.forms import StatementUploadForm
from account_statement.models import StatementSplitRun
from core.audit import log_action
from core.decorators import module_required
from core.models import AuditLog

PREVIEW_LIMIT = 60


@module_required("account_statement")
def index(request):
    form = StatementUploadForm()
    runs = StatementSplitRun.objects.select_related("created_by")[:15]
    return render(request, "account_statement/index.html", {"form": form, "runs": runs})


@module_required("account_statement", edit=True)
def run_view(request):
    if request.method != "POST":
        return redirect("account_statement:index")
    form = StatementUploadForm(request.POST, request.FILES)
    if not form.is_valid():
        runs = StatementSplitRun.objects.select_related("created_by")[:15]
        return render(request, "account_statement/index.html", {"form": form, "runs": runs})

    f = form.cleaned_data["statement_file"]
    try:
        rows = parse_statement(f)
    except Exception as exc:  # noqa: BLE001
        messages.error(request, f"تعذّرت قراءة الملف: {exc}")
        log_action(request, AuditLog.Action.ERROR, str(exc), module_code="account_statement")
        return redirect("account_statement:index")

    if not rows:
        messages.error(request, "لم يتم العثور على أي حركات صالحة داخل الملف.")
        return redirect("account_statement:index")

    result = split_by_currency(rows)
    summary_json = {
        code: {
            "label": s["label"], "count": s["count"],
            "total_debit": float(s["total_debit"]), "total_credit": float(s["total_credit"]),
            "balance": float(s["balance"]),
            "balance_syp_new_equivalent": float(
                s.get("total_debit_syp_equivalent", s["total_debit"])
                - s.get("total_credit_syp_equivalent", s["total_credit"])
            ),
        }
        for code, s in result["summary"].items()
    }

    run = StatementSplitRun.objects.create(
        created_by=request.user, source_file_name=f.name,
        total_rows=result["total_rows"], summary_json=summary_json,
    )
    buf = build_workbook(result, {"file_name": f.name})
    run.result_file.save(f"فصل_عملات_{run.pk}.xlsx", ContentFile(buf.read()), save=True)

    log_action(request, AuditLog.Action.RUN, f"فصل عملات #{run.pk}", module_code="account_statement", meta={"run_id": run.pk})
    messages.success(request, "تم فصل كشف الحساب حسب العملة بنجاح.")

    def row_to_json(r):
        return {
            "date": r["date"], "voucher_no": r["voucher_no"], "narration": r["narration"],
            "debit": float(r["debit"]), "credit": float(r["credit"]),
            "currency_raw": r["currency_raw"], "category": r["category"],
        }

    request.session[f"stmt_preview_{run.pk}"] = {
        code: [row_to_json(r) for r in bucket_rows[:PREVIEW_LIMIT]]
        for code, bucket_rows in result["buckets"].items()
    }
    return redirect("account_statement:result", pk=run.pk)


@module_required("account_statement")
def result(request, pk):
    run = get_object_or_404(StatementSplitRun, pk=pk)
    preview = request.session.get(f"stmt_preview_{run.pk}", {})
    return render(request, "account_statement/result.html", {"run": run, "preview": preview})


@module_required("account_statement")
def download(request, pk):
    run = get_object_or_404(StatementSplitRun, pk=pk)
    if not run.result_file:
        raise Http404
    log_action(request, AuditLog.Action.EXPORT, f"تنزيل فصل عملات #{run.pk}", module_code="account_statement")
    return FileResponse(run.result_file.open("rb"), as_attachment=True, filename=f"فصل_عملات_{run.pk}.xlsx")
