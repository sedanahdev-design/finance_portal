import io

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

HEADER_FILL = PatternFill("solid", fgColor="1F2937")
HEADER_FONT = Font(color="FFFFFF", bold=True)
WARN_FILL = PatternFill("solid", fgColor="FEF3C7")

# ألوان/أنماط شيت "نهائي" (جدول عريض حسب المورد) — تصحيح 2026-08-31: أضيف
# بطلب المستخدم الصريح ليقابل شيت "نهائي" الموجود بملفه المرجعي الشهري
# (صف لكل مندوب، وعمود مبيعات/نسبة/عمولة متكرر لكل مورد/شركة). النطاق هنا
# مقصور على ما تحسبه وحدة العمولات فعلياً (مبيعات/نسبة/عمولة لكل مندوب×
# شركة، بالإضافة لإجمالي المبيعات والعمولات) — بلا أي من الأعمدة اليدوية
# الأربعة الموجودة بملف المستخدم (الراتب الثابت/سلف/مسحوبات شخصية/خصم
# الذمم/خصم التحصيل/المستحق/الصافي)، لأن هذه القيم لا تُدخَل حالياً بأي
# ملف يُرفع للتطبيق — بتأكيد صريح من المستخدم أن النطاق المطلوب حالياً هو
# القسم المحسوب فقط.
COMPANY_BLOCK_FILL = PatternFill("solid", fgColor="374151")
TOTAL_BLOCK_FILL = PatternFill("solid", fgColor="1F2937")
GRAND_TOTAL_FILL = PatternFill("solid", fgColor="D1D5DB")
GRAND_TOTAL_FONT = Font(bold=True)
THIN_BORDER = Border(
    left=Side(style="thin", color="D1D5DB"), right=Side(style="thin", color="D1D5DB"),
    top=Side(style="thin", color="D1D5DB"), bottom=Side(style="thin", color="D1D5DB"),
)
MONEY_FORMAT = "#,##0.00"
PCT_FORMAT = "0.00%"


def _header(ws, headers):
    ws.append(headers)
    r = ws.max_row
    for c in range(1, len(headers) + 1):
        cell = ws.cell(row=r, column=c)
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
        cell.alignment = Alignment(horizontal="center", wrap_text=True)
    ws.freeze_panes = f"A{r + 1}"


def _write_wide_final_sheet(wb, rep_commissions):
    """شيت "نهائي" — جدول عريض: صف لكل مندوب، وكتلة 3 أعمدة (المبيعات/
    النسبة/العمولة) لكل شركة/مورد ظهرت عند أي مندوب، بترتيب أبجدي موحّد
    عبر كل الصفوف (خلافاً لملف المستخدم المرجعي حيث الترتيب غير موحّد
    وأسماء الأعمدة متكررة بلا تمييز) — مع رأسين: رأس علوي بعنوان الشركة
    ممتد فوق أعمدتها الثلاثة (merge)، ورأس فرعي يوضّح كل عمود. يُضاف عمودا
    إجمالي مبيعات/عمولة كل مندوب في النهاية، وصف "الإجمالي" في آخر الشيت
    لكل عمود (شركة بشركة، وإجمالياً). انظر تعليق أعلى الملف لسبب اقتصار
    النطاق على الأعمدة المحسوبة فعلياً من ملفات المبيعات/المرتجعات/النسب.
    """
    ws = wb.create_sheet("نهائي")
    ws.sheet_view.rightToLeft = True

    companies = sorted({company for data in rep_commissions.values() for company in data["companies"]})
    reps = sorted(rep_commissions.items())

    # --- الرأسان ---
    # ملاحظة: تُطبَّق التنسيقات (fill/font/alignment) فقط على "خلية المرساة"
    # (أعلى-يسار) لكل نطاق مدمج — خلايا المدى المدموج الأخرى تصبح كائنات
    # MergedCell لا تدعم تعيين نمط مباشر في openpyxl (وحتى لو دعمته، Excel
    # يعرض تنسيق خلية المرساة فقط لأي نطاق مدموج).
    header_anchor_style = {"fill": HEADER_FILL, "font": HEADER_FONT,
                            "alignment": Alignment(horizontal="center", vertical="center", wrap_text=True)}

    def _style_anchor(cell):
        cell.fill = header_anchor_style["fill"]
        cell.font = header_anchor_style["font"]
        cell.alignment = header_anchor_style["alignment"]

    rep_header = ws.cell(row=1, column=1, value="اسم المندوب / الكول سنتر")
    ws.merge_cells(start_row=1, end_row=2, start_column=1, end_column=1)
    _style_anchor(rep_header)

    col = 2
    for company in companies:
        company_header = ws.cell(row=1, column=col, value=company)
        ws.merge_cells(start_row=1, end_row=1, start_column=col, end_column=col + 2)
        _style_anchor(company_header)
        for c, label in enumerate(["المبيعات", "النسبة", "العمولة"]):
            cell = ws.cell(row=2, column=col + c, value=label)
            cell.fill = COMPANY_BLOCK_FILL
            cell.font = HEADER_FONT
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        col += 3
    total_sales_col = col
    total_commission_col = col + 1
    total_sales_header = ws.cell(row=1, column=total_sales_col, value="إجمالي المبيعات")
    ws.merge_cells(start_row=1, end_row=2, start_column=total_sales_col, end_column=total_sales_col)
    _style_anchor(total_sales_header)
    total_commission_header = ws.cell(row=1, column=total_commission_col, value="إجمالي العمولة")
    ws.merge_cells(start_row=1, end_row=2, start_column=total_commission_col, end_column=total_commission_col)
    _style_anchor(total_commission_header)
    last_col = total_commission_col
    ws.freeze_panes = "B3"

    # --- صفوف المندوبين ---
    company_totals = {c: {"sales": 0.0, "commission": 0.0} for c in companies}
    grand_sales = grand_commission = 0.0
    row_idx = 3
    for rep, data in reps:
        ws.cell(row=row_idx, column=1, value=rep)
        col = 2
        for company in companies:
            c = data["companies"].get(company)
            if c is not None:
                sales_v, rate_v, comm_v = float(c["sales"]), c["rate"], float(c["commission"])
                ws.cell(row=row_idx, column=col, value=sales_v).number_format = MONEY_FORMAT
                rate_cell = ws.cell(row=row_idx, column=col + 1)
                if rate_v is None:
                    rate_cell.value = "غير معروفة"
                else:
                    rate_cell.value = float(rate_v)
                    rate_cell.number_format = PCT_FORMAT
                ws.cell(row=row_idx, column=col + 2, value=comm_v).number_format = MONEY_FORMAT
                company_totals[company]["sales"] += sales_v
                company_totals[company]["commission"] += comm_v
            col += 3
        total_sales_v, total_commission_v = float(data["total_sales"]), float(data["total_commission"])
        ws.cell(row=row_idx, column=total_sales_col, value=total_sales_v).number_format = MONEY_FORMAT
        ws.cell(row=row_idx, column=total_commission_col, value=total_commission_v).number_format = MONEY_FORMAT
        grand_sales += total_sales_v
        grand_commission += total_commission_v
        for c in range(1, last_col + 1):
            ws.cell(row=row_idx, column=c).border = THIN_BORDER
        row_idx += 1

    # --- صف الإجمالي ---
    ws.cell(row=row_idx, column=1, value="الإجمالي")
    col = 2
    for company in companies:
        ws.cell(row=row_idx, column=col, value=company_totals[company]["sales"]).number_format = MONEY_FORMAT
        ws.cell(row=row_idx, column=col + 2, value=company_totals[company]["commission"]).number_format = MONEY_FORMAT
        col += 3
    ws.cell(row=row_idx, column=total_sales_col, value=grand_sales).number_format = MONEY_FORMAT
    ws.cell(row=row_idx, column=total_commission_col, value=grand_commission).number_format = MONEY_FORMAT
    for c in range(1, last_col + 1):
        cell = ws.cell(row=row_idx, column=c)
        cell.fill = GRAND_TOTAL_FILL
        cell.font = GRAND_TOTAL_FONT
        cell.border = THIN_BORDER

    ws.column_dimensions["A"].width = 28
    for c in range(2, last_col + 1):
        ws.column_dimensions[get_column_letter(c)].width = 14
    ws.column_dimensions[get_column_letter(total_sales_col)].width = 18
    ws.column_dimensions[get_column_letter(total_commission_col)].width = 18


def build_workbook(rep_commissions, company_breakdown, summary):
    wb = Workbook()

    ws0 = wb.active
    ws0.title = "الملخص"
    ws0.sheet_view.rightToLeft = True
    _header(ws0, ["عدد المندوبين/الكول سنتر", "إجمالي المبيعات", "إجمالي العمولات",
                  "شركات بلا نسبة معروفة"])
    ws0.append([
        summary["reps_count"], float(summary["total_sales"]), float(summary["total_commission"]),
        summary["unrated_companies_count"],
    ])
    for i, w in enumerate([22, 20, 20, 20], start=1):
        ws0.column_dimensions[get_column_letter(i)].width = w
    if summary["unrated_companies_count"]:
        ws0.append([])
        ws0.append(["تنبيه: توجد شركات في ملف الحركة غير موجودة في جدول نسب العمولات، عمولتها احتُسبت صفراً. راجع شيت 'شركات بلا نسبة'."])

    ws_final = wb.create_sheet("النهائي (صافي المندوب)")
    ws_final.sheet_view.rightToLeft = True
    _header(ws_final, ["اسم المندوب / الكول سنتر", "إجمالي المبيعات (صافي المرتجعات)", "إجمالي العمولة المستحقة"])
    unrated_set = set()
    for rep, data in sorted(rep_commissions.items()):
        ws_final.append([
            rep, float(data["total_sales"]), float(data["total_commission"]),
        ])
        if data.get("unrated_companies"):
            unrated_set.update(data["unrated_companies"])
    for i, w in enumerate([28, 26, 20], start=1):
        ws_final.column_dimensions[get_column_letter(i)].width = w

    ws_detail = wb.create_sheet("تفصيل حسب الشركة")
    ws_detail.sheet_view.rightToLeft = True
    _header(ws_detail, ["اسم المندوب / الكول سنتر", "الشركة", "المبيعات", "النسبة", "العمولة"])
    for rep, data in sorted(rep_commissions.items()):
        for company, c in sorted(data["companies"].items()):
            ws_detail.append([
                rep, company, float(c["sales"]),
                f"{float(c['rate']) * 100:.2f}%" if c["rate"] is not None else "غير معروفة",
                float(c["commission"]),
            ])
    for i, w in enumerate([28, 30, 16, 12, 16], start=1):
        ws_detail.column_dimensions[get_column_letter(i)].width = w

    ws_supplier = wb.create_sheet("تفصيل حسب المورد والشركة")
    ws_supplier.sheet_view.rightToLeft = True
    _header(ws_supplier, ["المورّد/الشركة", "إجمالي المبيعات (كل المندوبين)", "إجمالي العمولة (كل المندوبين)", "عدد سطور مندوب×شركة"])
    for company, c in sorted(company_breakdown.items(), key=lambda kv: kv[1]["commission"], reverse=True):
        ws_supplier.append([
            company, float(c["sales"]), float(c["commission"]), c["reps_count"],
        ])
    for i, w in enumerate([30, 24, 22, 20], start=1):
        ws_supplier.column_dimensions[get_column_letter(i)].width = w

    _write_wide_final_sheet(wb, rep_commissions)

    if unrated_set:
        ws_u = wb.create_sheet("شركات بلا نسبة")
        ws_u.sheet_view.rightToLeft = True
        _header(ws_u, ["اسم الشركة"])
        for c in sorted(unrated_set):
            ws_u.append([c])
        ws_u.column_dimensions["A"].width = 34

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf
