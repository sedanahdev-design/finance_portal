import io

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

HEADER_FILL = PatternFill("solid", fgColor="1F2937")
HEADER_FONT = Font(color="FFFFFF", bold=True)
OK_FILL = PatternFill("solid", fgColor="E7F7EF")
BAD_FILL = PatternFill("solid", fgColor="FDEAEA")
FOUND_DIFF_DATE_FILL = PatternFill("solid", fgColor="FDE9C8")  # برتقالي: موجود بمبلغ مطابق لكن بتاريخ مختلف


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
    s = result["summary"]

    ws0 = wb.active
    ws0.title = "الملخص"
    ws0.sheet_view.rightToLeft = True
    for row in [
        ["ملف مشروع دواك", meta.get("dawak_file_name", "")],
        ["ملف كشف حساب هبة", meta.get("hiba_file_name", "")],
        ["", ""],
        ["عدد الصيدليات", s["pharmacies_count"]],
        ["صيدليات متطابقة", s["matched_count"]],
        ["صيدليات غير متطابقة", s["mismatched_count"]],
        ["إجمالي فرق الصيدليات غير المتطابقة", float(s["mismatched_amount"])],
        ["", ""],
        ["إجمالي مدين دواك (كل الصيدليات)", float(s["dawak_total_debit"])],
        ["إجمالي دائن دواك (كل الصيدليات)", float(s["dawak_total_credit"])],
        ["", ""],
        ["إجمالي مدين كشف حساب هبة", float(s["hiba_total_debit"])],
        ["إجمالي دائن كشف حساب هبة", float(s["hiba_total_credit"])],
        ["رصيد كشف حساب هبة", float(s["hiba_balance"])],
    ]:
        ws0.append(row)
    ws0.column_dimensions["A"].width = 40
    ws0.column_dimensions["B"].width = 26

    ws1 = wb.create_sheet("مطابقة الصيدليات")
    ws1.sheet_view.rightToLeft = True
    _header(ws1, ["رمز الصيدلية", "اسم الصيدلية", "إجمالي البون (مدين)", "إجمالي المرتجع الوهمي (دائن)",
                  "الفرق", "الحالة (حسابنا)", "علامة النظام المصدر"])
    for p in result["pharmacies"]:
        ws1.append([
            p["code"], p["name"], float(p["total_debit"]), float(p["total_credit"]), float(p["difference"]),
            "مطابق" if p["matched"] else "غير مطابق",
            "غير مطابق" if p["source_flagged_mismatch"] else "مطابق",
        ])
        ws1.cell(row=ws1.max_row, column=6).fill = OK_FILL if p["matched"] else BAD_FILL
    for i, w in enumerate([14, 40, 20, 24, 14, 18, 20], start=1):
        ws1.column_dimensions[get_column_letter(i)].width = w

    ws2 = wb.create_sheet("تفاصيل الحركات")
    ws2.sheet_view.rightToLeft = True
    _header(ws2, ["رمز الصيدلية", "اسم الصيدلية", "التاريخ", "رقم السند", "البيان", "مدين", "دائن"])
    for p in result["pharmacies"]:
        for r in p["rows"]:
            ws2.append([p["code"], p["name"], r["date"], r["voucher_no"], r["narration"], float(r["debit"]), float(r["credit"])])
    for i, w in enumerate([14, 34, 12, 12, 50, 14, 14], start=1):
        ws2.column_dimensions[get_column_letter(i)].width = w

    # ---------------- مطابقة الحركات دواك ⇄ هبة (إضافة لاحقة) ----------------
    payments = result.get("payments")
    if payments is not None:
        ps = payments["summary"]
        pay_headers = ["الاتجاه", "تاريخ دواك", "رقم سند دواك", "بيان دواك", "المبلغ",
                       "تاريخ هبة", "رقم سند هبة", "بيان هبة", "فرق الأيام", "ملاحظات"]
        dir_label = {
            "dawak_debit_hiba_credit": "مدين دواك ⇄ دائن هبة",
            "dawak_credit_hiba_debit": "دائن دواك ⇄ مدين هبة",
        }

        def _entry_date_s(e):
            if e is None:
                return ""
            return e["entry_date"].isoformat() if e["entry_date"] else (e["raw_date"] or "")

        def _write_pairs(ws, pairs, fill):
            for p in pairs:
                a, b = p["a"], p["b"]
                ws.append([
                    dir_label.get(p["direction"], p["direction"]),
                    _entry_date_s(a), a["voucher_no"] if a else "", a["narration"] if a else "",
                    float(p["amount"]),
                    _entry_date_s(b), b["voucher_no"] if b else "", b["narration"] if b else "",
                    p["day_diff"] if p["day_diff"] is not None else "",
                    p["note"],
                ])
            for r in range(2, ws.max_row + 1):
                for c in range(1, len(pay_headers) + 1):
                    ws.cell(row=r, column=c).fill = fill
            for i, w in enumerate([20, 12, 12, 40, 14, 12, 12, 40, 10, 46], start=1):
                ws.column_dimensions[get_column_letter(i)].width = w

        ws3 = wb.create_sheet("مطابقة الدفعات دواك⇄هبة")
        ws3.sheet_view.rightToLeft = True
        _header(ws3, pay_headers)
        _write_pairs(ws3, payments["matched"], OK_FILL)

        # فئة مستقلة (وليست "فرق"): موجود بنفس المبلغ لكن بتاريخ مختلف — فحص ثانوي
        # حسب طلب المستخدم، حتى لا تُخفى المعلومة بأنها "غير موجودة" بالخطأ.
        ws4 = wb.create_sheet("موجود بتاريخ مختلف")
        ws4.sheet_view.rightToLeft = True
        _header(ws4, pay_headers)
        _write_pairs(ws4, payments["found_diff_date"], FOUND_DIFF_DATE_FILL)

        ws5 = wb.create_sheet("فرق حقيقي دواك⇄هبة")
        ws5.sheet_view.rightToLeft = True
        _header(ws5, pay_headers)
        _write_pairs(ws5, payments["true_diff"], BAD_FILL)

        # صفوف إضافية بالملخص لهذه المطابقة
        ws0.append(["", ""])
        ws0.append(["مطابقة الحركات دواك ⇄ هبة", ""])
        ws0.append(["عدد حركات دواك", ps["dawak_entries_count"]])
        ws0.append(["عدد حركات هبة", ps["hiba_entries_count"]])
        ws0.append(["حركات متطابقة", ps["matched_count"]])
        ws0.append(["   منها: نفس التاريخ", ps["matched_same_day"]])
        ws0.append(["   منها: بفارق تاريخ", ps["matched_date_diff"]])
        ws0.append(["موجود بنفس المبلغ بتاريخ مختلف (ليست فرقاً)", ps["found_diff_date_count"]])
        ws0.append(["   إجمالي مبلغها", float(ps["found_diff_date_amount"])])
        ws0.append(["فرق حقيقي (لا يوجد المبلغ إطلاقاً عند الطرف الآخر)", ps["true_diff_count"]])
        ws0.append(["   إجمالي مبلغها", float(ps["true_diff_amount"])])

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf
