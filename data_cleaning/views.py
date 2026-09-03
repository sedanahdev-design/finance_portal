from decimal import Decimal

from django.contrib import messages
from django.core.files.base import ContentFile
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render

from core.audit import log_action
from core.decorators import module_required
from core.models import AuditLog
from data_cleaning.engine import (
    combine, parse_discount_ledger, parse_receivables_ledger, parse_sales_or_returns, summarize,
)
from data_cleaning.excel_export import build_workbook
from data_cleaning.forms import DataCleaningUploadForm
from data_cleaning.models import DataCleaningRun

PREVIEW_LIMIT = 60


@module_required("data_cleaning")
def index(request):
    form = DataCleaningUploadForm()
    runs = DataCleaningRun.objects.select_related("created_by")[:15]
    return render(request, "data_cleaning/index.html", {"form": form, "runs": runs})


@module_required("data_cleaning", edit=True)
def run_view(request):
    if request.method != "POST":
        return redirect("data_cleaning:index")
    form = DataCleaningUploadForm(request.POST, request.FILES)
    if not form.is_valid():
        runs = DataCleaningRun.objects.select_related("created_by")[:15]
        return render(request, "data_cleaning/index.html", {"form": form, "runs": runs})

    d = form.cleaned_data
    try:
        sales = parse_sales_or_returns(d["sales_file"], is_return=False)
        returns = parse_sales_or_returns(d["returns_file"], is_return=True)
        discount_rows = parse_discount_ledger(d["discount_file"]) if d.get("discount_file") else []
        receivables_lists = []
        for key in ("receivables_file_1", "receivables_file_2"):
            if d.get(key):
                receivables_lists.append(parse_receivables_ledger(d[key]))
    except Exception as exc:  # noqa: BLE001
        messages.error(request, f"تعذّرت قراءة أحد الملفات: {exc}")
        log_action(request, AuditLog.Action.ERROR, str(exc), module_code="data_cleaning")
        return redirect("data_cleaning:index")

    combined = combine(sales, returns, receivables_lists)
    s = summarize(combined, discount_rows)

    run = DataCleaningRun.objects.create(
        created_by=request.user, total_rows=s["total_rows"],
        sales_rows=len(sales), returns_rows=len(returns),
        receivables_rows=sum(len(x) for x in receivables_lists),
        discount_rows=s["discount_rows"], total_deferred_value=Decimal(s["total_deferred_value"]),
    )
    buf = build_workbook(combined, discount_rows, s, {})
    run.result_file.save(f"تنظيف_داتا_{run.pk}.xlsx", ContentFile(buf.read()), save=True)

    log_action(request, AuditLog.Action.RUN, f"تنظيف داتا #{run.pk}", module_code="data_cleaning", meta={"run_id": run.pk})
    messages.success(request, f"تم تجهيز {s['total_rows']} سطر بيانات نظيفة بنجاح.")

    request.session[f"clean_preview_{run.pk}"] = [
        {"invoice": r["invoice"], "customer": r["customer"], "cost_center": r["cost_center"],
         "deferred_value": str(r["deferred_value"]), "delivery_date": r["delivery_date"], "zone": r["zone"]}
        for r in combined[:PREVIEW_LIMIT]
    ]
    return redirect("data_cleaning:result", pk=run.pk)


@module_required("data_cleaning")
def result(request, pk):
    run = get_object_or_404(DataCleaningRun, pk=pk)
    preview = request.session.get(f"clean_preview_{run.pk}", [])
    return render(request, "data_cleaning/result.html", {"run": run, "preview": preview})


@module_required("data_cleaning")
def download(request, pk):
    run = get_object_or_404(DataCleaningRun, pk=pk)
    if not run.result_file:
        raise Http404
    log_action(request, AuditLog.Action.EXPORT, f"تنزيل تنظيف داتا #{run.pk}", module_code="data_cleaning")
    return FileResponse(run.result_file.open("rb"), as_attachment=True, filename=f"تنظيف_داتا_{run.pk}.xlsx")
