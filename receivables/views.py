from decimal import Decimal

from django.contrib import messages
from django.core.files.base import ContentFile
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render

from core.audit import log_action
from core.decorators import module_required
from core.models import AuditLog
from receivables.engine import compute_person_breakdown, parse_ledger, reconcile
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
    person_breakdown = compute_person_breakdown(result)
    s = result["summary"]

    run = ReceivablesRun.objects.create(
        created_by=request.user, source_file_name=f.name,
        total_rows=s["total_rows"], linked_rows=s["linked_rows"], unlinked_rows=s["unlinked_rows"],
        groups_count=s["groups_count"], matched_groups=s["matched_groups"], mismatched_groups=s["mismatched_groups"],
        mismatched_amount=Decimal(s["mismatched_amount"]),
        solo_mismatched_groups=s["solo_mismatched_groups"], shared_mismatched_groups=s["shared_mismatched_groups"],
        name_linked_groups=s["name_linked_groups"], persons_count=len(person_breakdown),
    )
    buf = build_workbook(result, {"file_name": f.name}, person_breakdown=person_breakdown)
    run.result_file.save(f"مطابقة_ذمم_{run.pk}.xlsx", ContentFile(buf.read()), save=True)

    log_action(request, AuditLog.Action.RUN, f"مطابقة ذمم #{run.pk}", module_code="receivables", meta={"run_id": run.pk})
    if s["shared_mismatched_groups"]:
        messages.warning(
            request,
            f"توجد {s['solo_mismatched_groups']} مجموعة فردية غير متطابقة، بالإضافة إلى "
            f"{s['shared_mismatched_groups']} مجموعة \"مشتركة\" بين أكثر من موزّع تحتاج مراجعة يدوية "
            f"لأن فرقها لا يُحتسب ضمن مجموع أي موزّع بعينه.",
        )
    elif s["mismatched_groups"]:
        messages.warning(request, f"توجد {s['mismatched_groups']} مجموعة غير متطابقة تحتاج مراجعة.")
    else:
        messages.success(request, "تمت المطابقة بنجاح، جميع الكشوفات متطابقة.")

    def _ident(g):
        return ", ".join(g["statement_numbers"]) if g["statement_numbers"] else (", ".join(g["statement_names"]) or "—")

    def grp_json(g):
        return {
            "identifier": _ident(g), "identifier_kind": "رقم" if g["statement_numbers"] else "اسم",
            "statement_numbers": g["statement_numbers"], "statement_names": g["statement_names"],
            "persons": g["persons"], "is_shared": g["is_shared"], "subaccounts": g["subaccounts"],
            "total_debit": str(g["total_debit"]), "total_credit": str(g["total_credit"]),
            "difference": str(g["difference"]), "matched": g["matched"], "rows_count": len(g["rows"]),
        }

    def person_json(name, b):
        return {
            "name": name, "deficit_total": str(b["deficit_total"]), "excess_total": str(b["excess_total"]),
            "net_total": str(b["net_total"]), "deficit_count": len(b["deficit_groups"]),
            "excess_count": len(b["excess_groups"]), "shared_count": len(b["shared_groups"]),
            "unlinked_count": len(b["unlinked_rows"]),
        }

    request.session[f"recv_preview_{run.pk}"] = {
        "solo_mismatched": [grp_json(g) for g in result["solo_mismatched_groups"][:PREVIEW_LIMIT]],
        "shared_mismatched": [grp_json(g) for g in result["shared_mismatched_groups"][:PREVIEW_LIMIT]],
        "unlinked": [{"date": r["date"], "voucher_no": r["voucher_no"], "narration": r["narration"],
                       "person": r["person"], "debit": str(r["debit"]), "credit": str(r["credit"])}
                      for r in result["unlinked"][:PREVIEW_LIMIT]],
        "persons": [person_json(name, b) for name, b in person_breakdown.items()],
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
