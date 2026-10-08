from decimal import Decimal

from django.contrib import messages
from django.core.files.base import ContentFile
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render

from argivit_compare.engine import ExchangeRateRange, build_result
from argivit_compare.excel_export import build_workbook
from argivit_compare.forms import ArgivitCompareUploadForm
from argivit_compare.models import ArgivitCompareRun
from core.audit import log_action
from core.decorators import module_required
from core.models import AuditLog


@module_required("argivit_compare")
def index(request):
    form = ArgivitCompareUploadForm()
    runs = ArgivitCompareRun.objects.select_related("created_by")[:15]
    return render(request, "argivit_compare/index.html", {"form": form, "runs": runs})


def _rate_range_from_form(cleaned) -> ExchangeRateRange:
    if cleaned["rate_mode"] == "fixed":
        return ExchangeRateRange.fixed(cleaned["rate_fixed"])
    return ExchangeRateRange.ranged(cleaned["rate_min"], cleaned["rate_max"])


@module_required("argivit_compare", edit=True)
def run_view(request):
    if request.method != "POST":
        return redirect("argivit_compare:index")
    form = ArgivitCompareUploadForm(request.POST, request.FILES)
    if not form.is_valid():
        runs = ArgivitCompareRun.objects.select_related("created_by")[:15]
        return render(request, "argivit_compare/index.html", {"form": form, "runs": runs})

    cd = form.cleaned_data
    movement_f, price_f, ledger_f = cd["movement_file"], cd["price_file"], cd["ledger_file"]
    wholesale_f = cd.get("wholesale_file")
    rate_range = _rate_range_from_form(cd)

    try:
        result = build_result(movement_f, price_f, ledger_f, rate_range, wholesale_file=wholesale_f)
    except Exception as exc:  # noqa: BLE001
        messages.error(request, f"تعذّرت قراءة الملفات: {exc}")
        log_action(request, AuditLog.Action.ERROR, str(exc), module_code="argivit_compare")
        return redirect("argivit_compare:index")

    s = result["summary"]
    run = ArgivitCompareRun.objects.create(
        created_by=request.user,
        movement_file_name=movement_f.name, price_file_name=price_f.name, ledger_file_name=ledger_f.name,
        wholesale_file_name=wholesale_f.name if wholesale_f else "",
        rate_mode=cd["rate_mode"], rate_lo=Decimal(rate_range.lo), rate_hi=Decimal(rate_range.hi),
        movement_rows_count=s["movement_rows_count"],
        tier1_count=s["tier1_count"], tier2_count=s["tier2_count"],
        tier3_count=s["tier3_count"], tier4_count=s["tier4_count"], unmatched_count=s["unmatched_count"],
        retail_matched_count=s["retail_matched_count"], retail_mismatched_count=s["retail_mismatched_count"],
        retail_no_counterpart_count=s["retail_no_counterpart_count"],
        wholesale_matched_count=s["wholesale_matched_count"], wholesale_mismatched_count=s["wholesale_mismatched_count"],
        wholesale_no_counterpart_count=s["wholesale_no_counterpart_count"],
    )

    buf = build_workbook(result, {
        "movement_file_name": movement_f.name, "price_file_name": price_f.name,
        "ledger_file_name": ledger_f.name, "wholesale_file_name": wholesale_f.name if wholesale_f else "",
    })
    run.result_file.save(f"مطابقة_ارجيفيت_{run.pk}.xlsx", ContentFile(buf.read()), save=True)

    log_action(request, AuditLog.Action.RUN, f"مطابقة أسعار الارجيفيت #{run.pk}", module_code="argivit_compare", meta={"run_id": run.pk})

    msgs = []
    if s["unmatched_count"]:
        msgs.append(f"توجد {s['unmatched_count']} حركة لم تُطابَق بأي من المراحل الأربع — راجع شيت 'غير مطابقين بكل الطرق السابقة'.")
    if s["retail_mismatched_count"]:
        msgs.append(f"توجد {s['retail_mismatched_count']} حالة (زبون×مادة) غير متطابقة بين المبيع والمرتجع (مفرق).")
    if s["wholesale_mismatched_count"]:
        msgs.append(f"توجد {s['wholesale_mismatched_count']} حالة (زبون×مادة) غير متطابقة بين المبيع والمرتجع (جملة).")
    if msgs:
        messages.warning(request, " ".join(msgs))
    else:
        messages.success(request, "كل الحركات مطابقة سعرياً، وكل حالات المبيع/المرتجع متطابقة.")

    def _tier_preview(match_rows, limit=40):
        out = []
        for m in match_rows[:limit]:
            r = m.row
            out.append({
                "invoice": r.invoice, "date": r.date, "customer": r.customer, "item": r.item,
                "qty": str(r.qty), "gifts": str(r.gifts), "unit_price": str(r.unit_price),
                "basis": m.basis, "lo": str(m.expected_lo), "hi": str(m.expected_hi),
            })
        return out

    def _group_preview(groups, limit=40):
        out = []
        for g in groups[:limit]:
            out.append({"customer": g.customer, "item": g.item, "reasons": g.reasons})
        return out

    pm = result["price_match"]
    request.session[f"argivit_tier1_{run.pk}"] = _tier_preview(pm.tier1)
    request.session[f"argivit_tier2_{run.pk}"] = _tier_preview(pm.tier2)
    request.session[f"argivit_tier3_{run.pk}"] = _tier_preview(pm.tier3_retail)
    request.session[f"argivit_tier4_{run.pk}"] = _tier_preview(pm.tier4_special)
    request.session[f"argivit_unmatched_{run.pk}"] = [
        {"invoice": r.invoice, "date": r.date, "customer": r.customer, "item": r.item,
         "qty": str(r.qty), "unit_price": str(r.unit_price), "total_price": str(r.total_price)}
        for r in pm.unmatched[:40]
    ]
    request.session[f"argivit_retail_mismatched_{run.pk}"] = _group_preview(result["retail_reconciliation"]["mismatched"])
    if result.get("wholesale_reconciliation") is not None:
        request.session[f"argivit_wholesale_mismatched_{run.pk}"] = _group_preview(result["wholesale_reconciliation"]["mismatched"])

    return redirect("argivit_compare:result", pk=run.pk)


@module_required("argivit_compare")
def result(request, pk):
    run = get_object_or_404(ArgivitCompareRun, pk=pk)
    ctx = {
        "run": run,
        "tier1_preview": request.session.get(f"argivit_tier1_{run.pk}", []),
        "tier2_preview": request.session.get(f"argivit_tier2_{run.pk}", []),
        "tier3_preview": request.session.get(f"argivit_tier3_{run.pk}", []),
        "tier4_preview": request.session.get(f"argivit_tier4_{run.pk}", []),
        "unmatched_preview": request.session.get(f"argivit_unmatched_{run.pk}", []),
        "retail_mismatched_preview": request.session.get(f"argivit_retail_mismatched_{run.pk}", []),
        "wholesale_mismatched_preview": request.session.get(f"argivit_wholesale_mismatched_{run.pk}", []),
    }
    return render(request, "argivit_compare/result.html", ctx)


@module_required("argivit_compare")
def download(request, pk):
    run = get_object_or_404(ArgivitCompareRun, pk=pk)
    if not run.result_file:
        raise Http404
    log_action(request, AuditLog.Action.EXPORT, f"تنزيل مطابقة أسعار الارجيفيت #{run.pk}", module_code="argivit_compare")
    return FileResponse(run.result_file.open("rb"), as_attachment=True, filename=f"مطابقة_ارجيفيت_{run.pk}.xlsx")
