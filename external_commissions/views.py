from decimal import Decimal

from django.contrib import messages
from django.core.files.base import ContentFile
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render

from core.audit import log_action
from core.decorators import module_required
from core.models import AuditLog
from external_commissions.engine import build_summary, parse_distributor_ledger
from external_commissions.excel_export import build_workbook
from external_commissions.models import ExternalCommissionRun


@module_required("external_commissions")
def index(request):
    runs = ExternalCommissionRun.objects.select_related("created_by")[:15]
    return render(request, "external_commissions/index.html", {"runs": runs})


@module_required("external_commissions", edit=True)
def run_view(request):
    if request.method != "POST":
        return redirect("external_commissions:index")

    files = request.FILES.getlist("distributor_files")
    if not files:
        messages.error(request, "الرجاء رفع ملف واحد على الأقل (ملف ذمم كل موزّع).")
        return redirect("external_commissions:index")

    distributors = []
    for f in files:
        try:
            distributors.append(parse_distributor_ledger(f))
        except Exception as exc:  # noqa: BLE001
            messages.error(request, f"تعذّرت قراءة الملف {f.name}: {exc}")
            log_action(request, AuditLog.Action.ERROR, str(exc), module_code="external_commissions")
            return redirect("external_commissions:index")

    summary = build_summary(distributors)

    run = ExternalCommissionRun.objects.create(
        created_by=request.user, distributors_count=summary["distributors_count"],
        total_debit=Decimal(summary["total_debit"]), total_credit=Decimal(summary["total_credit"]),
        total_commission=Decimal(summary["total_commission"]),
    )
    buf = build_workbook(distributors, summary)
    run.result_file.save(f"عمولات_موزعين_خارجيين_{run.pk}.xlsx", ContentFile(buf.read()), save=True)

    log_action(request, AuditLog.Action.RUN, f"عمولات موزعين خارجيين #{run.pk}",
               module_code="external_commissions", meta={"run_id": run.pk})
    messages.success(request, f"تم احتساب عمولات {summary['distributors_count']} موزّع بنجاح.")

    request.session[f"extcomm_preview_{run.pk}"] = [
        {"name": d["name"], "opening_balance": str(d["opening_balance"]), "total_debit": str(d["total_debit"]),
         "total_credit": str(d["total_credit"]), "total_returns": str(d["total_returns"]),
         "total_sales_excluded": str(d["total_sales_excluded"]), "commission_base": str(d["commission_base"]),
         "commission": str(d["commission"]), "closing_balance": str(d["closing_balance"])}
        for d in distributors
    ]
    return redirect("external_commissions:result", pk=run.pk)


@module_required("external_commissions")
def result(request, pk):
    run = get_object_or_404(ExternalCommissionRun, pk=pk)
    preview = request.session.get(f"extcomm_preview_{run.pk}", [])
    return render(request, "external_commissions/result.html", {"run": run, "preview": preview})


@module_required("external_commissions")
def download(request, pk):
    run = get_object_or_404(ExternalCommissionRun, pk=pk)
    if not run.result_file:
        raise Http404
    log_action(request, AuditLog.Action.EXPORT, f"تنزيل عمولات موزعين خارجيين #{run.pk}", module_code="external_commissions")
    return FileResponse(run.result_file.open("rb"), as_attachment=True, filename=f"عمولات_موزعين_خارجيين_{run.pk}.xlsx")
