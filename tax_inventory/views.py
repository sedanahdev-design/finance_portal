from decimal import Decimal

from django.contrib import messages
from django.core.files.base import ContentFile
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render

from core.audit import log_action
from core.decorators import module_required
from core.models import AuditLog
from tax_inventory.engine import (
    build_detail_rows,
    parse_inventory,
    parse_sales_detail_rows,
    parse_sales_quantities,
    reconcile,
)
from tax_inventory.excel_export import build_workbook
from tax_inventory.forms import TaxInventoryUploadForm
from tax_inventory.models import TaxInventoryRun

PREVIEW_LIMIT = 60


@module_required("tax_inventory")
def index(request):
    form = TaxInventoryUploadForm()
    runs = TaxInventoryRun.objects.select_related("created_by")[:15]
    return render(request, "tax_inventory/index.html", {"form": form, "runs": runs})


@module_required("tax_inventory", edit=True)
def run_view(request):
    if request.method != "POST":
        return redirect("tax_inventory:index")
    form = TaxInventoryUploadForm(request.POST, request.FILES)
    if not form.is_valid():
        runs = TaxInventoryRun.objects.select_related("created_by")[:15]
        return render(request, "tax_inventory/index.html", {"form": form, "runs": runs})

    over3_f = form.cleaned_data["over3_file"]
    under3_f = form.cleaned_data["under3_file"]
    sales_f = form.cleaned_data["sales_file"]

    try:
        over3_items = parse_inventory(over3_f)
        under3_items = parse_inventory(under3_f)
        sales_detail_rows = parse_sales_detail_rows(sales_f)
    except Exception as exc:  # noqa: BLE001
        messages.error(request, f"تعذّرت قراءة الملفات: {exc}")
        log_action(request, AuditLog.Action.ERROR, str(exc), module_code="tax_inventory")
        return redirect("tax_inventory:index")

    result = reconcile(over3_items, under3_items, sales_detail_rows)
    detail_rows = build_detail_rows(sales_detail_rows, over3_items)
    s = result["summary"]

    run = TaxInventoryRun.objects.create(
        created_by=request.user,
        over3_file_name=over3_f.name, under3_file_name=under3_f.name, sales_file_name=sales_f.name,
        items_over3=s["items_over3"], items_matched_in_sales=s["items_matched_in_sales"],
        total_inventory_qty=Decimal(str(s["total_inventory_qty"])),
        total_sold_qty=Decimal(str(s["total_sold_qty"])),
        total_final_qty=s["total_final_qty"], cross_listed_count=s["cross_listed_count"],
        capped_items_count=s["capped_items_count"], approx_items_count=s["approx_items_count"],
    )
    buf = build_workbook(result, {
        "over3_file_name": over3_f.name, "under3_file_name": under3_f.name, "sales_file_name": sales_f.name,
    }, detail_rows=detail_rows)
    run.result_file.save(f"مطابقة_جرد_{run.pk}.xlsx", ContentFile(buf.read()), save=True)

    log_action(request, AuditLog.Action.RUN, f"مطابقة جرد #{run.pk}", module_code="tax_inventory", meta={"run_id": run.pk})
    if s["capped_items_count"]:
        messages.success(
            request,
            f"تمت المطابقة بنجاح. {s['capped_items_count']} مادة تجاوز فيها إجمالي أمين 8 سقف أمين 9، "
            f"فاعتُمد لها أفضل مزيج من الصيدليات (أقصى استخدام ممكن) — راجع عمود الملاحظات وشيت "
            f"'التوزيع على الصيدليات' في ملف النتيجة.",
        )
    else:
        messages.success(request, "تمت عملية مطابقة الجرد بنجاح.")
    request.session[f"tax_inv_preview_{run.pk}"] = result["rows"][:PREVIEW_LIMIT]
    return redirect("tax_inventory:result", pk=run.pk)


@module_required("tax_inventory")
def result(request, pk):
    run = get_object_or_404(TaxInventoryRun, pk=pk)
    preview = request.session.get(f"tax_inv_preview_{run.pk}", [])
    return render(request, "tax_inventory/result.html", {"run": run, "preview": preview})


@module_required("tax_inventory")
def download(request, pk):
    run = get_object_or_404(TaxInventoryRun, pk=pk)
    if not run.result_file:
        raise Http404
    log_action(request, AuditLog.Action.EXPORT, f"تنزيل نتيجة مطابقة جرد #{run.pk}", module_code="tax_inventory")
    return FileResponse(run.result_file.open("rb"), as_attachment=True, filename=f"مطابقة_جرد_{run.pk}.xlsx")
