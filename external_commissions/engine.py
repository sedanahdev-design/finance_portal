"""محرك عمولات الموزعين الخارجيين (الفكرة التاسعة).

لكل موزّع خارجي ملف "سحب من العميل" (دفتر أستاذ) يحوي:
    - مدين  = كشوفات (Statements) بذمّة الموزّع
    - دائن  = مبيعات و/أو مرتجعات محصّلة لصالح الموزّع (مجمّعة معاً في
              عمود دائن واحد داخل دفتر الأستاذ الخام، دون تمييز مباشر)

--- تعديل متعمّد بطلب المستخدم بتاريخ 2026-08-26 -----------------------
المعادلة القديمة (تم التحقق سابقاً من مطابقتها التامة لأرصدة المصدر):
    العمولة = ((مبيع + مرتجع) − كشوفات) × 3%
    أي: العمولة = (إجمالي الدائن كاملاً − إجمالي المدين) × 3%

المعادلة الجديدة (الحالية):
    العمولة = (مرتجع − كشوفات) × 3%
    أي: تم إسقاط بند "مبيع" من المعادلة نهائياً، وأصبح أساس العمولة هو
    المرتجعات فقط مقابل الكشوفات — بناءً على طلب صريح من المستخدم.

مصدر "مرتجع" بعد التعديل: بما أن دفتر الأستاذ الخام لا يميّز داخلياً بين
"دائن-مبيعات" و"دائن-مرتجعات" (كلاهما يظهر كعمود دائن واحد، بلا عمود
رقمي مستقل للمرتجعات)، طلب المستخدم استخراج المرتجعات من نص عمود
"البيان" الحر بدل الاعتماد على عمود الدائن كاملاً. تم التحقق من هذه
الآلية على ملف مرجعي فعلي لموزّع خارجي حقيقي (شادي حسن، من قائمة
"موزعين خارجيين" الموثّقة) حيث تظهر حركات الدائن العادية (مبيعات) ببيان
فارغ، بينما تحمل حركة المرتجع الوحيدة في ذلك الملف بياناً نصّياً صريحاً
يساوي "مرتجع". لذلك: أي حركة دائن يحتوي نص "البيان" فيها على الكلمة
"مرتجع" تُحتسب ضمن المرتجعات (أساس العمولة الجديد)؛ وأي حركة دائن أخرى
(بيان فارغ أو بيان لا يحوي "مرتجع") تُعامَل كـ"مبيع" وتُستبعد من أساس
العمولة بالكامل — لكنها لا تُحذف من البيانات: تبقى ظاهرة في صفوف
الحركات (كل حركة دائن موسومة بنوعها: مرتجع / مبيع) وضمن إجمالي منفصل
"total_sales_excluded" في نتيجة كل موزّع، حتى لا يُخفى أي رقم عن المستخدم
(اتساقاً مع سياسة المشروع بعدم إسقاط أي صف بيانات بصمت).

الرصيد الافتتاحي ("الرصيد السابق") يُعرض كرصيد دوّار مرحّل من الشهر
السابق، ولا يدخل في حساب عمولة الشهر الحالي (لأنه من المفترض أن عمولته
احتُسبت سابقاً)، لكنه يظهر في التقرير لإظهار الرصيد الختامي الصحيح.
ملاحظة: الرصيد الختامي (closing_balance) يبقى محسوباً من إجمالي الدائن
الكامل (مبيعات + مرتجعات) والمدين كما هو فعلياً في دفتر الأستاذ — فهو
يعكس حقيقة الحساب المالي وليس أساس العمولة، ولم يتأثر بهذا التعديل.
"""

import re
from decimal import Decimal

import openpyxl

COMMISSION_RATE = Decimal("0.03")

HEADER_SIGNATURE = {"رقم السند", "مدين", "دائن", "التاريخ"}
STOP_MARKERS = {"المجموع", "الرصيد النهائي"}

# كلمة تُستخدم لاستخراج حركات "مرتجع" من نص عمود "البيان" الحر ضمن حركات
# الدائن (راجع توثيق التعديل بتاريخ 2026-08-26 في أعلى الملف). أي حركة
# دائن لا يحتوي بيانها على هذه الكلمة تُعتبر "مبيع" وتُستبعد من أساس العمولة.
RETURN_MARKER = "مرتجع"


def _clean(v):
    if v is None:
        return ""
    return str(v).strip() if isinstance(v, str) else v


def _to_decimal(v):
    if v is None or v == "":
        return Decimal("0")
    if isinstance(v, (int, float, Decimal)):
        return Decimal(str(v)).quantize(Decimal("0.01"))
    s = str(v).replace(",", "").strip()
    m = re.match(r"^-?\d+(\.\d+)?", s)
    if not m:
        return Decimal("0")
    try:
        return Decimal(m.group(0)).quantize(Decimal("0.01"))
    except Exception:  # noqa: BLE001
        return Decimal("0")


def _distributor_name_from_account(all_rows):
    for row in all_rows[:6]:
        if row and row[0] and "اسم الحساب" in str(row[0]):
            m = re.search(r"-(.+)$", str(row[0]))
            if m:
                return m.group(1).strip()
    return None


def parse_distributor_ledger(file_obj, display_name=None):
    wb = openpyxl.load_workbook(file_obj, data_only=True, read_only=True)
    ws = wb[wb.sheetnames[0]]
    all_rows = list(ws.iter_rows(values_only=True))
    wb.close()

    name = display_name or _distributor_name_from_account(all_rows) or "موزّع غير محدد"

    header_idx = header = None
    for i, row in enumerate(all_rows):
        cells = {str(_clean(c)) for c in row if c is not None}
        if HEADER_SIGNATURE.issubset(cells):
            header_idx, header = i, [str(_clean(c)) for c in row]
            break
    if header_idx is None:
        raise ValueError(f"لم يتم العثور على صف العناوين المتوقع داخل ملف {name}.")

    col = {h: header.index(h) for h in header if h}

    def get(row, key):
        idx = col.get(key)
        if idx is None or idx >= len(row):
            return None
        return row[idx]

    opening_balance = Decimal("0")
    debit_rows, credit_rows = [], []
    closing_balance_from_source = None

    for row in all_rows[header_idx + 1:]:
        if row is None or all(c in (None, "") for c in row):
            continue
        first_cell = _clean(row[0])
        if str(first_cell) in STOP_MARKERS:
            # صف الإجمالي/الرصيد النهائي له بنية مختلفة عن باقي الصفوف
            # (بلا رقم سند): [التسمية، مجموع مدين، مجموع دائن، الرصيد، ...]
            if len(row) > 3:
                closing_balance_from_source = _to_decimal(row[3])
            if first_cell == "الرصيد النهائي":
                break
            continue
        if first_cell == "الرصيد السابق":
            debit0 = _to_decimal(get(row, "مدين"))
            credit0 = _to_decimal(get(row, "دائن"))
            opening_balance = credit0 - debit0
            continue

        debit = _to_decimal(get(row, "مدين"))
        credit = _to_decimal(get(row, "دائن"))
        if debit == 0 and credit == 0:
            continue

        raw_ref = get(row, "البيان")
        reference = _clean(raw_ref)
        voucher_no = _clean(get(row, "رقم السند"))
        date = _clean(get(row, "التاريخ"))

        if debit:
            debit_rows.append({
                "voucher_no": voucher_no, "reference": reference, "date": date,
                "amount": debit,
            })
        if credit:
            # هل هذه الحركة "مرتجع" بحسب نص البيان؟ (راجع توثيق التعديل
            # بتاريخ 2026-08-26 في أعلى الملف). أي حركة دائن أخرى تُعامَل
            # كـ"مبيع" وتُستبعد من أساس العمولة، مع بقائها ظاهرة هنا موسومة.
            is_return = RETURN_MARKER in str(reference)
            credit_rows.append({
                "voucher_no": voucher_no, "reference": reference, "date": date,
                "amount": credit,
                "kind": "مرتجع" if is_return else "مبيع (مستبعد من العمولة)",
                "is_return": is_return,
            })

    total_debit = sum((r["amount"] for r in debit_rows), Decimal("0"))
    total_credit = sum((r["amount"] for r in credit_rows), Decimal("0"))
    total_returns = sum((r["amount"] for r in credit_rows if r["is_return"]), Decimal("0"))
    total_sales_excluded = total_credit - total_returns

    # المعادلة الجديدة (بديلة عن ((مبيع + مرتجع) − كشوفات) × 3% القديمة):
    # العمولة = (مرتجع − كشوفات) × 3% — بند "مبيع" مُسقَط بالكامل.
    commission_base = total_returns - total_debit
    commission = (commission_base * COMMISSION_RATE).quantize(Decimal("0.01"))

    # الرصيد الختامي يعكس واقع دفتر الأستاذ المالي كاملاً (مبيعات + مرتجعات
    # مقابل الكشوفات)، وليس أساس العمولة — لذلك لا يتأثر بإسقاط "مبيع" أعلاه.
    closing_balance = closing_balance_from_source if closing_balance_from_source is not None else (
        opening_balance + total_credit - total_debit
    )

    return {
        "name": name,
        "opening_balance": opening_balance,
        "debit_rows": debit_rows,
        "credit_rows": credit_rows,
        "total_debit": total_debit,
        "total_credit": total_credit,
        "total_returns": total_returns,
        "total_sales_excluded": total_sales_excluded,
        "commission_base": commission_base,
        "commission_rate": COMMISSION_RATE,
        "commission": commission,
        "closing_balance": closing_balance,
    }


def build_summary(distributors):
    return {
        "distributors_count": len(distributors),
        "total_commission": sum((d["commission"] for d in distributors), Decimal("0")),
        "total_debit": sum((d["total_debit"] for d in distributors), Decimal("0")),
        "total_credit": sum((d["total_credit"] for d in distributors), Decimal("0")),
        "total_returns": sum((d["total_returns"] for d in distributors), Decimal("0")),
        "total_sales_excluded": sum((d["total_sales_excluded"] for d in distributors), Decimal("0")),
    }
