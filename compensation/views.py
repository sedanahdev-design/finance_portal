from decimal import Decimal

from django.contrib import messages
from django.core.files.base import ContentFile
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render

from compensation.engine import parse_claims_table, process
from compensation.excel_export import build_workbook
from compensation.forms import CompensationUploadForm
from compensation.models import CompensationRun
from core.audit import log_action
from core.decorators import module_required
from core.models import AuditLog

PREVIEW_LIMIT = 60


@module_required("compensation")
def index(request):
    form = CompensationUploadForm()
    runs = CompensationRun.objects.select_related("created_by")[:15]
    return render(request, "compensation/index.html", {"form": form, "runs": runs})


@module_required("compensation", edit=True)
def run_view(request):
    if request.method != "POST":
        return redirect("compensation:index")
    form = CompensationUploadForm(request.POST, request.FILES)
    if not form.is_valid():
        runs = CompensationRun.objects.select_related("created_by")[:15]
        return render(request, "compensation/index.html", {"form": form, "runs": runs})

    f = form.cleaned_data["movement_file"]
    try:
        f.seek(0)
        claims_table = parse_claims_table(f)
        f.seek(0)
        result = process(f)
    except Exception as exc:  # noqa: BLE001
        messages.error(request, f"تعذّرت قراءة الملف: {exc}")
        log_action(request, AuditLog.Action.ERROR, str(exc), module_code="compensation")
        return redirect("compensation:index")

    run = CompensationRun.objects.create(
        created_by=request.user, source_file_name=f.name,
        raw_row_count=result["raw_row_count"], offer_row_count=result["offer_row_count"],
        ignored_items_count=result["ignored_items_count"],
        excluded_mabee_rows_count=result["excluded_mabee_rows_count"],
        cancelled_mabee_pairs=result["cancelled_mabee_pairs"],
        cancelled_pairs=result["cancelled_pairs"],
        unmatched_returns_count=result["unmatched_returns_count"],
        excluded_nonpositive_rows_count=result["excluded_nonpositive_rows_count"],
        merged_zero_qty_rows_count=result["merged_zero_qty_rows"],
        unmerged_zero_qty_rows_count=result["unmerged_zero_qty_rows_count"],
        pool_matches_count=result["pool_matches_count"],
        pool_matched_rows_count=result["pool_matched_rows_count"],
        items_count=result["items_count"], groups_count=result["groups_count"],
        ineligible_groups_count=len(result["ineligible_groups"]),
        total_qty=Decimal(str(result["total_qty"])), total_gifts=Decimal(str(result["total_gifts"])),
        total_formula_result=Decimal(str(result["total_formula_result"])),
        total_claim_value=Decimal(str(result["total_claim_value"])),
    )
    buf = build_workbook(result, claims_table)
    run.result_file.save(f"تعويضات_فيتا_فارما_{run.pk}.xlsx", ContentFile(buf.read()), save=True)

    log_action(request, AuditLog.Action.RUN, f"تعويضات فيتا فارما #{run.pk}", module_code="compensation", meta={"run_id": run.pk})
    if result["ineligible_groups"]:
        messages.warning(
            request,
            f"توجد {len(result['ineligible_groups'])} حزمة (مادة × عرض مفرق) بلا قيمة "
            f"\"عرض مفرق\" صالحة — احتُسبت مطالبتها كمجموع كل هداياها مباشرة (بلا معادلة). "
            f"راجع شيت \"حزم بلا عرض مفرق صالح\" داخل ملف النتيجة.",
        )
    else:
        messages.success(request, f"تمت معالجة {result['items_count']} مادة بنجاح، وكل الحزم محتسبة.")
    if result["ignored_items_count"]:
        messages.info(
            request,
            f"تم استبعاد {result['ignored_items_count']} مادة بالكامل لعدم وجود أي عرض مميز لها في "
            f"الملف (بطلب المستخدم) — راجع شيت \"مواد مستبعدة (بلا عرض مميز)\".",
        )
    if result["excluded_mabee_rows_count"] or result["cancelled_mabee_pairs"]:
        messages.info(
            request,
            f"فواتير \"م. مبيع\": {result['cancelled_mabee_pairs']} زوج (مع سطر بيع مطابق) أُلغي "
            f"بالكامل، و{result['excluded_mabee_rows_count']} سطر استُبعد بمفرده — راجع شيت "
            f"\"فواتير م. مبيع مستبعدة\".",
        )
    if result["pool_matches_count"]:
        messages.info(
            request,
            f"تم إلغاء {result['pool_matches_count']} سطر تصحيح/مرتجع كبير الحجم (بلا فاتورة بيع "
            f"واحدة تطابقه) مقابل تجميع {result['pool_matched_rows_count']} فاتورة بيع أصغر "
            f"(مجموع كمياتها وهداياها يطابقه تماماً) — راجع شيت \"مطابقات تجميع فواتير البيع\".",
        )
    if result["excluded_nonpositive_rows_count"]:
        messages.info(
            request,
            f"تم استبعاد {result['excluded_nonpositive_rows_count']} سطر كان صافيه (الهدايا − ناتج "
            f"معادلته) سالباً أو صفرياً — راجع شيت \"أسطر صافٍ سالب أو صفري مستبعدة\".",
        )
    if result["merged_zero_qty_rows"]:
        messages.info(
            request,
            f"تم دمج هدايا {result['merged_zero_qty_rows']} سطر كميته = صفر مع سطر آخر لنفس الزبون "
            f"ثم حذف سطر الكمية=صفر.",
        )
    if result["unmerged_zero_qty_rows_count"]:
        messages.warning(
            request,
            f"توجد {result['unmerged_zero_qty_rows_count']} سطر كمية=صفر بلا سطر آخر لنفس الزبون "
            f"لدمج هداياه معه — راجع شيت \"أسطر كمية=صفر بلا زبون آخر\".",
        )
    items_preview = []
    for item, groups in sorted(result["per_item"].items())[:PREVIEW_LIMIT]:
        qty_sum = sum((g.qty for g in groups), Decimal("0"))
        gifts_sum = sum((g.gifts for g in groups), Decimal("0"))
        formula_sum = sum((g.formula_result or Decimal("0")) for g in groups)
        value_sum = sum((g.claim_value or Decimal("0")) for g in groups)
        items_preview.append({
            "item": item, "groups": len(groups), "qty": str(qty_sum),
            "gifts": str(gifts_sum), "formula": str(formula_sum), "value": str(value_sum),
        })

    request.session[f"comp_preview_{run.pk}"] = items_preview
    return redirect("compensation:result", pk=run.pk)


@module_required("compensation")
def result(request, pk):
    run = get_object_or_404(CompensationRun, pk=pk)
    preview = request.session.get(f"comp_preview_{run.pk}", [])
    return render(request, "compensation/result.html", {"run": run, "preview": preview})


@module_required("compensation")
def download(request, pk):
    run = get_object_or_404(CompensationRun, pk=pk)
    if not run.result_file:
        raise Http404
    log_action(request, AuditLog.Action.EXPORT, f"تنزيل تعويضات فيتا فارما #{run.pk}", module_code="compensation")
    return FileResponse(run.result_file.open("rb"), as_attachment=True, filename=f"تعويضات_فيتا_فارما_{run.pk}.xlsx")
