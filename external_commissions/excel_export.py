import io

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

HEADER_FILL = PatternFill("solid", fgColor="1F2937")
HEADER_FONT = Font(color="FFFFFF", bold=True)


def _header(ws, headers):
    ws.append(headers)
    r = ws.max_row
    for c in range(1, len(headers) + 1):
        cell = ws.cell(row=r, column=c)
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
        cell.alignment = Alignment(horizontal="center", wrap_text=True)
    ws.freeze_panes = f"A{r + 1}"


def build_workbook(distributors, summary):
    wb = Workbook()
    ws0 = wb.active
    ws0.title = "الملخص"
    ws0.sheet_view.rightToLeft = True
    ws0.append(["معادلة العمولة: (مرتجع − كشوفات) × 3%  — تم إسقاط بند \"مبيع\" من المعادلة "
                "بطلب المستخدم بتاريخ 2026-08-26 (المعادلة القديمة كانت (مبيع + مرتجع − كشوفات) × 3%)."])
    ws0.append([])
    _header(ws0, ["الموزّع", "الرصيد الافتتاحي (دوّار)", "إجمالي الكشوفات (مدين)",
                  "إجمالي الدائن (مبيعات + مرتجعات)", "منها: مرتجعات (أساس العمولة)",
                  "منها: مبيعات (مستبعدة من العمولة)", "أساس العمولة (مرتجع − مدين)",
                  "نسبة العمولة", "العمولة", "الرصيد الختامي"])
    for d in distributors:
        ws0.append([
            d["name"], float(d["opening_balance"]), float(d["total_debit"]), float(d["total_credit"]),
            float(d["total_returns"]), float(d["total_sales_excluded"]),
            float(d["commission_base"]), f"{float(d['commission_rate'])*100:.0f}%",
            float(d["commission"]), float(d["closing_balance"]),
        ])
    ws0.append([])
    ws0.append(["الإجمالي", "", float(summary["total_debit"]), float(summary["total_credit"]),
                float(summary["total_returns"]), float(summary["total_sales_excluded"]), "", "",
                float(summary["total_commission"]), ""])
    for i, w in enumerate([26, 20, 20, 20, 18, 22, 20, 14, 16, 18], start=1):
        ws0.column_dimensions[get_column_letter(i)].width = w

    for d in distributors:
        ws = wb.create_sheet(d["name"][:28] or "موزّع")
        ws.sheet_view.rightToLeft = True
        ws.append([f"كشف حساب: {d['name']}"])
        ws.append(["الرصيد الافتتاحي (دوّار من الشهر السابق)", float(d["opening_balance"])])
        ws.append([])
        ws.append(["العمولة = (مرتجع − كشوفات) × 3%  — عمود \"النوع\" يوضّح أي حركة دائن اعتُبرت "
                    "مرتجعاً (تدخل في أساس العمولة) وأيها مبيع (مستبعد من العمولة، وليست محذوفة)."])
        ws.append(["قيمة الكشوفات (مدين)", None, None, "المبيعات + المرتجعات (دائن)"])
        _header(ws, ["رقم السند", "المرجع", "التاريخ", "المبلغ (مدين)", "",
                     "رقم السند", "المرجع", "التاريخ", "المبلغ (دائن)", "النوع"])
        max_len = max(len(d["debit_rows"]), len(d["credit_rows"]))
        for i in range(max_len):
            deb = d["debit_rows"][i] if i < len(d["debit_rows"]) else None
            cre = d["credit_rows"][i] if i < len(d["credit_rows"]) else None
            ws.append([
                deb["voucher_no"] if deb else "", deb["reference"] if deb else "",
                deb["date"] if deb else "", float(deb["amount"]) if deb else "",
                "",
                cre["voucher_no"] if cre else "", cre["reference"] if cre else "",
                cre["date"] if cre else "", float(cre["amount"]) if cre else "",
                cre["kind"] if cre else "",
            ])
        ws.append([])
        ws.append(["إجمالي مدين (كشوفات)", float(d["total_debit"]), "", "إجمالي دائن (مبيعات + مرتجعات)", float(d["total_credit"])])
        ws.append(["منها: مرتجعات (أساس العمولة)", float(d["total_returns"]), "", "منها: مبيعات (مستبعدة من العمولة)", float(d["total_sales_excluded"])])
        ws.append(["أساس العمولة (مرتجع − مدين)", float(d["commission_base"])])
        ws.append(["العمولة (3%)", float(d["commission"])])
        ws.append(["الرصيد الختامي", float(d["closing_balance"])])
        for i, w in enumerate([12, 30, 12, 14, 4, 12, 30, 12, 14, 22], start=1):
            ws.column_dimensions[get_column_letter(i)].width = w

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf
