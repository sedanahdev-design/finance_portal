import io

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

from distributor_commissions.engine import SITUATION_ALONE, SITUATION_GROUP, SITUATION_PAIR

HEADER_FILL = PatternFill("solid", fgColor="1F2937")
HEADER_FONT = Font(color="FFFFFF", bold=True)
FLAG_FILL = PatternFill("solid", fgColor="FDE68A")
SUBTOTAL_FILL = PatternFill("solid", fgColor="E5E7EB")

TIER_LABEL = {"car": "سيارة", "moto": "دراجة"}
SITUATION_ORDER = [SITUATION_ALONE, SITUATION_PAIR, SITUATION_GROUP]


def _header(ws, headers):
    ws.append(headers)
    r = ws.max_row
    for c in range(1, len(headers) + 1):
        cell = ws.cell(row=r, column=c)
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
        cell.alignment = Alignment(horizontal="center", wrap_text=True)
    ws.freeze_panes = f"A{r + 1}"


def build_workbook(parsed, result, summary, meta, situation_breakdown=None, return_situation_breakdown=None):
    wb = Workbook()

    ws0 = wb.active
    ws0.title = "الملخص"
    ws0.sheet_view.rightToLeft = True
    ws0.append(["ملخص عمولة تحصيل الموزعين الداخليين — نقدية + مرتجعات"])
    ws0.append([])
    ws0.append(["ملف الحركة", meta.get("ledger_file_name", "")])
    ws0.append(["عدد حركات التحصيل النقدي المحتسبة", summary["rows_count"]])
    ws0.append(["عدد حركات المرتجع المحتسبة", summary["return_rows_count"]])
    ws0.append(["عدد الموزعين", summary["distributors_count"]])
    ws0.append(["إجمالي عمولة التحصيل (قبل المرتجعات)", float(summary["collection_total"])])
    ws0.append(["إجمالي خصم المرتجعات", float(summary["return_total"])])
    ws0.append(["الصافي النهائي", float(summary["total_commission"])])
    ws0.append([])
    ws0.append(["حركات مستبعدة كلياً (بلا عمولة):"])
    ws0.append(["  — حركات حساب مستودع (عمود الحساب المقابل)", parsed.warehouse_excluded_count,
                float(parsed.warehouse_excluded_amount)])
    for marker, amt in sorted(parsed.excluded_marker_totals.items()):
        ws0.append([f"  — علامة غير-شخصية: {marker}", "", float(amt)])
    ws0.append([])
    if parsed.flagged_rows:
        ws0.append([f"⚠ يوجد {len(parsed.flagged_rows)} حركة تحتاج مراجعة يدوية — راجع شيت 'حركات للمراجعة'."])
    ws0.append(["ملاحظة: خصم المرتجعات نسبة ثابتة 0.5% لكل مشارك (وليس النسب المتدرجة"
                " المستخدمة في التحصيل النقدي) — بحسب مطابقة شيت 'تقرير نتيجة' المرجعي"
                " الذي زوّدنا به المستخدم للتحقق؛ راجع توثيق الكود لتفاصيل هذا القرار."])
    ws0.column_dimensions["A"].width = 46
    ws0.column_dimensions["B"].width = 16
    ws0.column_dimensions["C"].width = 16

    ws1 = wb.create_sheet("عمولة الموزعين (الصافي)")
    ws1.sheet_view.rightToLeft = True
    _header(ws1, ["اسم الموزع", "عمولة التحصيل النقدي", "خصم المرتجعات", "الصافي"])
    collection = result["collection_commission"]
    returns = result["return_commission"]
    for name in sorted(result["totals"]):
        ws1.append([
            name,
            float(collection.get(name, 0)),
            float(returns.get(name, 0)),
            float(result["totals"][name]),
        ])
    for i, w in enumerate([30, 20, 18, 16], start=1):
        ws1.column_dimensions[get_column_letter(i)].width = w

    ws2 = wb.create_sheet("تفصيل حركات التحصيل")
    ws2.sheet_view.rightToLeft = True
    _header(ws2, ["البيان", "المبلغ (مدين)", "عدد المشاركين", "المشاركون (اسم/فئة/مصدر)"])
    for row in parsed.collection_rows:
        parts_str = "، ".join(
            f"{p.name} ({TIER_LABEL.get(p.tier, p.tier)}"
            f"{'، من البيان' if p.role_col is None else ''})"
            for p in row.participants
        )
        ws2.append([row.bayan, float(row.debit), len(row.participants), parts_str])
    for i, w in enumerate([70, 16, 14, 60], start=1):
        ws2.column_dimensions[get_column_letter(i)].width = w

    ws3 = wb.create_sheet("تفصيل المرتجعات")
    ws3.sheet_view.rightToLeft = True
    _header(ws3, ["البيان", "المبلغ", "عدد المشاركين", "المشاركون"])
    for row in parsed.return_rows:
        parts_str = "، ".join(p.name for p in row.participants)
        ws3.append([row.bayan, float(row.amount), len(row.participants), parts_str])
    for i, w in enumerate([40, 16, 14, 60], start=1):
        ws3.column_dimensions[get_column_letter(i)].width = w

    # ------------------------------------------------------------------
    # تفصيل كل موزع حسب الحالة (منفرد / مع شخص آخر / مجموعة) — الطلب الجديد:
    # "تفصيل كل موزع منفرداً مع الربح المالي لكل حالة والعمولة لكل حالة".
    # سطر واحد لكل (موزع × حالة)؛ المجموع عبر الحالات الثلاث لكل موزع يساوي
    # عمولته الإجمالية في شيت "عمولة الموزعين (الصافي)" تماماً (لا تُغيَّر
    # النسب هنا إطلاقاً — فقط إعادة عرض لنفس الاحتساب بحسب الحالة).
    # ------------------------------------------------------------------
    ws5 = wb.create_sheet("تفصيل كل موزع حسب الحالة")
    ws5.sheet_view.rightToLeft = True
    _header(ws5, ["اسم الموزع", "الحالة", "عدد الحركات", "إجمالي المبلغ (مدين)", "العمولة"])
    situation_breakdown = situation_breakdown or {}
    for name in sorted(result["totals"]):
        situations = situation_breakdown.get(name, {})
        subtotal_count = 0
        subtotal_amount = 0.0
        subtotal_commission = 0.0
        for sit in SITUATION_ORDER:
            b = situations.get(sit, {"count": 0, "amount": 0, "commission": 0})
            ws5.append([name, sit, b["count"], float(b["amount"]), float(b["commission"])])
            subtotal_count += b["count"]
            subtotal_amount += float(b["amount"])
            subtotal_commission += float(b["commission"])
        r = ws5.max_row + 1
        ws5.append([name, "إجمالي الموزع (كل الحالات)", subtotal_count, subtotal_amount, subtotal_commission])
        for c in range(1, 6):
            ws5.cell(row=r, column=c).fill = SUBTOTAL_FILL
            ws5.cell(row=r, column=c).font = Font(bold=True)
    if not result["totals"]:
        ws5.append(["لا توجد بيانات."])
    for i, w in enumerate([30, 26, 14, 20, 16], start=1):
        ws5.column_dimensions[get_column_letter(i)].width = w

    ws5b = wb.create_sheet("تفصيل المرتجعات حسب الحالة")
    ws5b.sheet_view.rightToLeft = True
    ws5b.append(["ملاحظة: نسبة خصم المرتجع ثابتة 0.5% لكل مشارك بصرف النظر عن الحالة"
                 " (منفرد/مع غيره) — هذا الشيت يوضّح فقط توزّع عدد/مبلغ/خصم المرتجعات"
                 " على كل حالة لكل موزع للشفافية، وليس نسباً مختلفة حسب الحالة."])
    ws5b.append([])
    _header(ws5b, ["اسم الموزع", "الحالة", "عدد حركات المرتجع", "إجمالي مبلغ المرتجع", "خصم العمولة"])
    return_situation_breakdown = return_situation_breakdown or {}
    return_names = sorted(set(result["return_commission"]) | set(return_situation_breakdown))
    for name in return_names:
        situations = return_situation_breakdown.get(name, {})
        subtotal_count = 0
        subtotal_amount = 0.0
        subtotal_commission = 0.0
        for sit in SITUATION_ORDER:
            b = situations.get(sit, {"count": 0, "amount": 0, "commission": 0})
            ws5b.append([name, sit, b["count"], float(b["amount"]), float(b["commission"])])
            subtotal_count += b["count"]
            subtotal_amount += float(b["amount"])
            subtotal_commission += float(b["commission"])
        r = ws5b.max_row + 1
        ws5b.append([name, "إجمالي الموزع (كل الحالات)", subtotal_count, subtotal_amount, subtotal_commission])
        for c in range(1, 6):
            ws5b.cell(row=r, column=c).fill = SUBTOTAL_FILL
            ws5b.cell(row=r, column=c).font = Font(bold=True)
    if not return_names:
        ws5b.append(["لا توجد بيانات مرتجعات."])
    for i, w in enumerate([30, 26, 16, 20, 16], start=1):
        ws5b.column_dimensions[get_column_letter(i)].width = w

    ws4 = wb.create_sheet("حركات للمراجعة")
    ws4.sheet_view.rightToLeft = True
    _header(ws4, ["السبب", "البيان", "المبلغ", "الاسم/الأسماء"])
    for f in parsed.flagged_rows:
        r = ws4.max_row + 1
        ws4.append([f["reason"], f["bayan"], float(f["debit"]), f["name"]])
        for c in range(1, 5):
            ws4.cell(row=r, column=c).fill = FLAG_FILL
    if not parsed.flagged_rows:
        ws4.append(["لا توجد حركات مُعلَّمة للمراجعة في هذا التشغيل."])
    for i, w in enumerate([30, 60, 14, 30], start=1):
        ws4.column_dimensions[get_column_letter(i)].width = w

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf
