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


# أعمدة "الإضافات" الإضافية (تُضاف لشيت "نهائي" فقط عند رفع ملف إضافات
# فعلياً — انظر توثيق merge_additions في engine.py). الترتيب هنا يطابق
# حرفياً ترتيب أعمدة ملف المستخدم المرجعي "عمولات نهائي.xlsx" (الفريق/
# الراتب الثابت قبل كتل الشركات، وبقية الأعمدة بعد إجمالي المبيعات/العمولة)
# — هذا هو ترتيب "الفيشة" الذي اعتمده المستخدم أصلاً، فلا داعي لإعادة
# ترتيبه، فقط تمديده بنفس الأسلوب.
ADDITIONS_TAIL_LABELS = ["مرتجعات", "خصم التحصيل", "خصم الذمم", "مكافأة فيتا", "المستحق", "سلف", "الصافي"]
ADDITIONS_TAIL_KEYS = ["returns_deduction", "collection_deduction", "receivables_deduction",
                       "vita_bonus", "due", "advance", "net"]


def _write_wide_final_sheet(wb, rep_commissions, merged=None):
    """شيت "نهائي" — جدول عريض: صف لكل مندوب، وكتلة 3 أعمدة (المبيعات/
    النسبة/العمولة) لكل شركة/مورد ظهرت عند أي مندوب، بترتيب أبجدي موحّد
    عبر كل الصفوف (خلافاً لملف المستخدم المرجعي حيث الترتيب غير موحّد
    وأسماء الأعمدة متكررة بلا تمييز) — مع رأسين: رأس علوي بعنوان الشركة
    ممتد فوق أعمدتها الثلاثة (merge)، ورأس فرعي يوضّح كل عمود. يُضاف عمودا
    إجمالي مبيعات/عمولة كل مندوب في النهاية، وصف "الإجمالي" في آخر الشيت
    لكل عمود (شركة بشركة، وإجمالياً). انظر تعليق أعلى الملف لسبب اقتصار
    النطاق على الأعمدة المحسوبة فعلياً من ملفات المبيعات/المرتجعات/النسب.

    `merged` (اختياري، تصحيح 2026-09-27): ناتج commissions.engine.merge_additions
    — إن مُرِّر (رُفع ملف إضافات فعلياً)، تُضاف أعمدة "الفريق"/"الراتب
    الثابت" قبل كتل الشركات، وأعمدة "مرتجعات/خصم التحصيل/خصم الذمم/مكافأة
    فيتا/المستحق/سلف/الصافي" بعد إجمالي المبيعات/العمولة — بنفس ترتيب ملف
    المستخدم المرجعي. بلا ملف إضافات، الشيت يبقى كما كان تماماً (بلا أي
    تغيير في الشكل) لضمان عدم كسر أي تشغيل سابق."""
    ws = wb.create_sheet("نهائي")
    ws.sheet_view.rightToLeft = True

    has_additions = bool(merged)
    companies = sorted({company for data in rep_commissions.values() for company in data["companies"]})
    reps = sorted(set(rep_commissions) | (set(merged) if merged else set()))

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

    team_col = fixed_salary_col = None
    if has_additions:
        team_col = col
        team_header = ws.cell(row=1, column=col, value="الفريق")
        ws.merge_cells(start_row=1, end_row=2, start_column=col, end_column=col)
        _style_anchor(team_header)
        col += 1

        fixed_salary_col = col
        salary_header = ws.cell(row=1, column=col, value="الراتب الثابت")
        ws.merge_cells(start_row=1, end_row=2, start_column=col, end_column=col)
        _style_anchor(salary_header)
        col += 1

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
    col = total_commission_col + 1

    tail_cols = {}
    if has_additions:
        for label, key in zip(ADDITIONS_TAIL_LABELS, ADDITIONS_TAIL_KEYS):
            tail_cols[key] = col
            header = ws.cell(row=1, column=col, value=label)
            ws.merge_cells(start_row=1, end_row=2, start_column=col, end_column=col)
            _style_anchor(header)
            col += 1

    last_col = col - 1
    freeze_col = (fixed_salary_col + 1) if has_additions else 2
    ws.freeze_panes = f"{get_column_letter(freeze_col)}3"

    # --- صفوف المندوبين ---
    company_totals = {c: {"sales": 0.0, "commission": 0.0} for c in companies}
    tail_totals = {key: 0.0 for key in ADDITIONS_TAIL_KEYS}
    grand_sales = grand_commission = 0.0
    row_idx = 3
    for rep in reps:
        data = rep_commissions.get(rep)
        m = merged.get(rep) if merged else None
        ws.cell(row=row_idx, column=1, value=rep)
        if has_additions:
            ws.cell(row=row_idx, column=team_col, value=(m["team"] if m else "") or "")
            salary_cell = ws.cell(row=row_idx, column=fixed_salary_col, value=float(m["fixed_salary"]) if m else 0.0)
            salary_cell.number_format = MONEY_FORMAT
        col = (fixed_salary_col + 1) if has_additions else 2
        for company in companies:
            c = data["companies"].get(company) if data else None
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
        total_sales_v = float(data["total_sales"]) if data else 0.0
        total_commission_v = float(data["total_commission"]) if data else 0.0
        ws.cell(row=row_idx, column=total_sales_col, value=total_sales_v).number_format = MONEY_FORMAT
        ws.cell(row=row_idx, column=total_commission_col, value=total_commission_v).number_format = MONEY_FORMAT
        grand_sales += total_sales_v
        grand_commission += total_commission_v
        if has_additions and m:
            for key in ADDITIONS_TAIL_KEYS:
                v = float(m[key])
                ws.cell(row=row_idx, column=tail_cols[key], value=v).number_format = MONEY_FORMAT
                tail_totals[key] += v
        elif has_additions:
            # مندوب بلا صف إضافات: المستحق/الصافي = عمولته المحسوبة فقط
            fallback = {"returns_deduction": 0.0, "collection_deduction": 0.0, "receivables_deduction": 0.0,
                        "vita_bonus": 0.0, "due": total_commission_v, "advance": 0.0, "net": total_commission_v}
            for key in ADDITIONS_TAIL_KEYS:
                v = fallback[key]
                ws.cell(row=row_idx, column=tail_cols[key], value=v).number_format = MONEY_FORMAT
                tail_totals[key] += v
        for c in range(1, last_col + 1):
            ws.cell(row=row_idx, column=c).border = THIN_BORDER
        row_idx += 1

    # --- صف الإجمالي ---
    ws.cell(row=row_idx, column=1, value="الإجمالي")
    if has_additions:
        ws.cell(row=row_idx, column=fixed_salary_col, value=sum(
            float(merged[r]["fixed_salary"]) for r in reps if r in merged
        )).number_format = MONEY_FORMAT
    col = (fixed_salary_col + 1) if has_additions else 2
    for company in companies:
        ws.cell(row=row_idx, column=col, value=company_totals[company]["sales"]).number_format = MONEY_FORMAT
        ws.cell(row=row_idx, column=col + 2, value=company_totals[company]["commission"]).number_format = MONEY_FORMAT
        col += 3
    ws.cell(row=row_idx, column=total_sales_col, value=grand_sales).number_format = MONEY_FORMAT
    ws.cell(row=row_idx, column=total_commission_col, value=grand_commission).number_format = MONEY_FORMAT
    if has_additions:
        for key in ADDITIONS_TAIL_KEYS:
            ws.cell(row=row_idx, column=tail_cols[key], value=tail_totals[key]).number_format = MONEY_FORMAT
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
    if has_additions:
        ws.column_dimensions[get_column_letter(team_col)].width = 10
        ws.column_dimensions[get_column_letter(fixed_salary_col)].width = 14
        ws.column_dimensions[get_column_letter(tail_cols["due"])].width = 16
        ws.column_dimensions[get_column_letter(tail_cols["net"])].width = 16


def build_workbook(rep_commissions, company_breakdown, summary, merged=None):
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

    _write_wide_final_sheet(wb, rep_commissions, merged=merged)

    if unrated_set:
        ws_u = wb.create_sheet("شركات بلا نسبة")
        ws_u.sheet_view.rightToLeft = True
        _header(ws_u, ["اسم الشركة"])
        for c in sorted(unrated_set):
            ws_u.append([c])
        ws_u.column_dimensions["A"].width = 34

    # شيتا مراجعة "ملف الإضافات" (2026-09-27) — تُضافان فقط عند رفع ملف
    # إضافات فعلياً، بلا حذف صامت لأي طرف غير متطابق (انظر merge_additions
    # في engine.py).
    if merged:
        missing = sorted(rep for rep, m in merged.items() if not m["has_addition_row"])
        if missing:
            ws_missing = wb.create_sheet("مندوبون بلا صف إضافات")
            ws_missing.sheet_view.rightToLeft = True
            ws_missing.append([
                "هؤلاء المندوبون لهم عمولة محسوبة هذا الشهر لكن بلا صف مطابق بملف الإضافات — "
                "احتُسبت إضافاتهم صفراً (المستحق = عمولتهم المحسوبة فقط، الصافي = المستحق). "
                "راجع إن كان أحدهم يفترض أن يكون له راتب ثابت/خصومات لم تُرفع.",
            ])
            _header(ws_missing, ["اسم المندوب", "إجمالي العمولة المحسوبة"])
            for rep in missing:
                ws_missing.append([rep, float(rep_commissions[rep]["total_commission"])])
            for i, w in enumerate([28, 22], start=1):
                ws_missing.column_dimensions[get_column_letter(i)].width = w

        unmatched = sorted(rep for rep, m in merged.items() if not m["has_sales"])
        if unmatched:
            ws_unmatched = wb.create_sheet("أسماء بملف الإضافات غير مطابقة")
            ws_unmatched.sheet_view.rightToLeft = True
            ws_unmatched.append([
                "هذه الأسماء موجودة في ملف الإضافات لكن بلا أي مبيعات محتسبة لها هذا الشهر — إما "
                "مندوب فعلاً بلا مبيعات (إجازة مثلاً، فراتبه الثابت ما زال يُحتسب بلا مبيعات)، أو "
                "خطأ إملائي بالاسم يمنع مطابقته باسم المندوب في ملف الحركة. راجعها يدوياً.",
            ])
            _header(ws_unmatched, ["اسم المندوب (من ملف الإضافات)", "الراتب الثابت", "المستحق", "الصافي"])
            for rep in unmatched:
                m = merged[rep]
                ws_unmatched.append([rep, float(m["fixed_salary"]), float(m["due"]), float(m["net"])])
            for i, w in enumerate([28, 16, 16, 16], start=1):
                ws_unmatched.column_dimensions[get_column_letter(i)].width = w

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf
