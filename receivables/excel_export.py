import io

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

HEADER_FILL = PatternFill("solid", fgColor="1F2937")
HEADER_FONT = Font(color="FFFFFF", bold=True)
OK_FILL = PatternFill("solid", fgColor="E7F7EF")
BAD_FILL = PatternFill("solid", fgColor="FDEAEA")


def _header(ws, headers):
    ws.append(headers)
    for c in range(1, len(headers) + 1):
        cell = ws.cell(row=1, column=c)
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
        cell.alignment = Alignment(horizontal="center", wrap_text=True)
    ws.freeze_panes = "A2"


def build_workbook(result, meta):
    wb = Workbook()

    ws0 = wb.active
    ws0.title = "الملخص"
    ws0.sheet_view.rightToLeft = True
    s = result["summary"]
    for row in [
        ["الملف", meta.get("file_name", "")],
        ["إجمالي عدد الحركات", s["total_rows"]],
        ["حركات مرتبطة برقم بيان", s["linked_rows"]],
        ["حركات بلا رقم بيان (تحتاج مراجعة يدوية)", s["unlinked_rows"]],
        ["عدد مجموعات أرقام البيان", s["groups_count"]],
        ["مجموعات متطابقة", s["matched_groups"]],
        ["مجموعات غير متطابقة", s["mismatched_groups"]],
        ["إجمالي فرق المجموعات غير المتطابقة", float(s["mismatched_amount"])],
    ]:
        ws0.append(row)
    ws0.column_dimensions["A"].width = 42
    ws0.column_dimensions["B"].width = 24

    ws1 = wb.create_sheet("المطابقة حسب رقم البيان")
    ws1.sheet_view.rightToLeft = True
    _header(ws1, ["أرقام البيان", "الحسابات الفرعية", "إجمالي مدين", "إجمالي دائن (مجمّع)", "الفرق", "الحالة", "عدد الحركات"])
    for g in result["groups"]:
        ws1.append([
            ", ".join(g["statement_numbers"]) or "—",
            ", ".join(g["subaccounts"]),
            float(g["total_debit"]), float(g["total_credit"]), float(g["difference"]),
            "مطابق" if g["matched"] else "غير مطابق", len(g["rows"]),
        ])
        ws1.cell(row=ws1.max_row, column=6).fill = OK_FILL if g["matched"] else BAD_FILL
    for i, w in enumerate([20, 30, 16, 18, 14, 14, 12], start=1):
        ws1.column_dimensions[get_column_letter(i)].width = w

    ws2 = wb.create_sheet("تفاصيل الحركات")
    ws2.sheet_view.rightToLeft = True
    _header(ws2, ["أرقام البيان", "التاريخ", "رقم السند", "البيان", "الحساب الفرعي", "مدين", "دائن"])
    for g in result["groups"]:
        for r in g["rows"]:
            ws2.append([", ".join(g["statement_numbers"]), r["date"], r["voucher_no"], r["narration"],
                        r["subaccount"], float(r["debit"]), float(r["credit"])])
    for i, w in enumerate([18, 12, 12, 55, 26, 14, 14], start=1):
        ws2.column_dimensions[get_column_letter(i)].width = w

    ws3 = wb.create_sheet("حركات بلا رقم بيان")
    ws3.sheet_view.rightToLeft = True
    _header(ws3, ["التاريخ", "رقم السند", "البيان", "الحساب الفرعي", "مدين", "دائن"])
    for r in result["unlinked"]:
        ws3.append([r["date"], r["voucher_no"], r["narration"], r["subaccount"], float(r["debit"]), float(r["credit"])])
    for i, w in enumerate([12, 12, 55, 26, 14, 14], start=1):
        ws3.column_dimensions[get_column_letter(i)].width = w

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf
