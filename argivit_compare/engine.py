"""
منطق وحدة "مطابقة أسعار الارجيفيت (بالدولار) والمبيعات مع المرتجعات" —
بُنيت بتاريخ 2026-10-01 بطلب صريح من المستخدم، بعد تحليل الملفات الأربعة
الحقيقية المرفقة (قائمة أسعار الارجيفيت بالدولار، حركة يومية مفرق،
دفتر أستاذ الزبائن، حركة جملة) وجولتي أسئلة توضيحية حُسمت نتائجهما كما
يلي — كل قرار هنا قرار تصميم فعلي اتُّخذ أثناء البناء وليس افتراضاً
ضمنياً، فهو موثّق هنا ليُراجَع إن ظهر خلاف لاحقاً:

1. **الحقول الأربعة المطلوبة** تُقابل: (أ) ملف "الحركة اليومية" (مفرق) —
   بيع ومرتجع مادة الارجيفيت بالليرة، (ب) ملف "قائمة الأسعار" — أسعار
   مواد الارجيفيت بالدولار فقط من شيت "جرد المواد"، (ج) حقل "مواد
   دولار" = ملف دفتر أستاذ الزبائن نفسه (مؤكَّد من المستخدم صريحاً) —
   يُستخدَم **فقط** لمعرفة هل فاتورة/سطر معيّن دولاري وبأي سعر صرف،
   عبر عمود "أصل السند" (يحمل نفس صيغة رقم الفاتورة الموجودة بملف
   الحركة اليومية، مثل "ارجيفيت: 2011") وعمود "العملة الأصلية" الذي
   يحمل سعر الوحدة بالدولار وسعر الصرف معاً بخلية واحدة بصيغة
   "11.30 [$ 138.00]" — وليس كشف حساب عام يُستخدَم لأي مطابقة أخرى.
   (د) "سعر الصرف" — **مُدخَل يكتبه المستخدم بالواجهة، لا يُقرأ من أي
   ملف**: ثابت (رقم واحد) أو متغير (حد أدنى وحد أعلى)، لأن حساب نسبة
   (الإفرادي الفعلي ÷ سعر القائمة بالدولار) على الملف الحقيقي المرفق
   توزّع فعلياً بين 133 و140 تقريباً خلال نفس الشهر (وليس رقماً ثابتاً
   واحداً) — تأكيد مباشر من المستخدم بعد عرض هذا التوزيع عليه بالأرقام.

2. **ملف "مبيعات جملة مع المرتجعات"** مستقل تماماً عن الثلاثة أعلاه —
   مخصص للعملية الثالثة (مطابقة بيع/مرتجع الجملة) فقط، وهو ملف عام
   يحوي كل المواد (ليس الارجيفيت فقط)، فلا يدخل في مطابقة الأسعار.

3. **مراحل مطابقة السعر الافرادي** (للحركة اليومية مفرق، على كل سطر):
   - المرحلة 1 "مطابقين": الإفرادي الفعلي يقع ضمن
     [سعر القائمة×حد أدنى الصرف , سعر القائمة×حد أعلى الصرف].
   - المرحلة 2 "مطابقين بعد خصم الحسم" (لما تبقّى): السعر الإفرادي
     الفعّال = (السعر الإجمالي − الحسم) ÷ الكمية، يُفحَص بنفس النطاق.
   - المرحلة 3 "مطابق على العرض المفرق" (لما تبقّى، وله عرض مفرق
     صالح "رقم+رقم"): السعر المتوقع = سعر القائمة × (الرقم الأيسر ÷
     مجموع رقمي العرض) × نطاق الصرف، يُقارَن بالإفرادي الفعلي. تُرفَق
     بهذا الشيت أيضاً **نفس فحص "فيتا فارما"** (التزام الكميات
     والهدايا بالعروض المميزة حسب compensation/engine.py حرفياً، بلا
     أي تعديل على منطقه) كفحص تحقّق إضافي منفصل تماماً عن قرار
     المطابقة السعرية، لكل حزمة (مادة × عرض مفرق).
   - المرحلة 4 "مطابق على العرض المميز": نفس منطق المرحلة 3 بالضبط
     لكن باستخدام عمود "عرض مميز"/"عرض مميز1" بدل "عرض المفرق".
   - ما تبقّى بعد المراحل الأربع → "غير مطابقين بكل الطرق السابقة"
     بكل التفاصيل الخام للمراجعة اليدوية.

4. **مطابقة المبيعات مع المرتجعات حسب الزبون** (مفرق، نفس ملف الحركة
   اليومية): لكل (زبون × مادة) له سطر بيع وسطر مرتجع معاً، يُقارَن:
   مجموعة أسعار المرتجعات ضمن مجموعة أسعار المبيعات لنفس (زبون×مادة)،
   كذلك نسبة الحسم (الحسم÷السعر الإجمالي)، وأخيراً العملة (دولاري أم
   لا، عبر دفتر الأستاذ) — أي خلل بأي من الثلاثة يُدرَج بتنبيه يحدد
   بالضبط أي بُعد لم يتطابق. (زبون×مادة) بلا طرف مقابل (بيع بلا مرتجع
   أو العكس) تُعرَض بسبب "لا يوجد طرف مقابل ضمن هذا الملف" بدل افتراض
   خطأ — تحقّق فعلي أن بعض المرتجعات بالملف المرفق لا نظير لها أصلاً
   بنفس الشهر (مرتجع من شهر سابق).

5. **مطابقة بيع/مرتجع الجملة** (ملف "مبيعات جملة"، عام لكل المواد):
   لكل (زبون × مادة)، تُقارَن مجموعة كميات المرتجعات ضمن مجموعة كميات
   المبيعات، ونسبة الحسم كذلك (بلا فحص عملة — غير مطلوب هنا). فواتير
   البيع تبدأ بـ"ع.مبيع" والمرتجع بـ"م.مبيع" (مع تطبيع المسافات حول
   النقطة لاختلاف تباعدها الفعلي بالملف: "ع.مبيع ج" مقابل "م. مبيع ج").
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Optional

from compensation.engine import (
    MovementRow as VitaMovementRow,
    compute_claim_groups as vita_compute_claim_groups,
    has_special_offer as vita_has_special_offer,
)

OFFER_RE = re.compile(r"^\s*(\d+)\s*\+\s*(\d+)\s*$")
CURRENCY_CELL_RE = re.compile(r"^\s*([\d.,]+)\s*\[\s*\$\s*([\d.,]+)\s*\]\s*$")
SUMMARY_ROW_LABELS = {"مجموع المواد", "مجموع المواد السالبة", "المجموع النهائي", "الأسعار"}


def _clean(v):
    if v is None:
        return ""
    if isinstance(v, str):
        return v.strip()
    return v


def _to_decimal(v) -> Decimal:
    if v is None or v == "":
        return Decimal("0")
    if isinstance(v, Decimal):
        return v
    try:
        return Decimal(str(v).replace(",", ""))
    except InvalidOperation:
        return Decimal("0")


def _find_header(all_rows, required_cols, max_scan=12):
    for idx in range(min(max_scan, len(all_rows))):
        row = all_rows[idx]
        if not row:
            continue
        cells = {str(_clean(c)) for c in row if c is not None}
        if required_cols.issubset(cells):
            return idx, {str(_clean(c)): i for i, c in enumerate(row) if c is not None}
    raise ValueError("تعذّر العثور على صف العناوين المطلوب في الملف.")


def parse_offer_lr(raw) -> Optional[tuple]:
    """يرجع (الرقم الأيسر, الرقم الأيمن) **بالترتيب كما هو مكتوب حرفياً**
    (بعكس parse_offer بوحدة compensation التي ترجع صغير/كبير) — لأن
    معادلة هذه الوحدة تحتاج "الرقم اليساري" بالتحديد كما وصفه المستخدم."""
    text = str(_clean(raw))
    if text in ("", "-", "0", "None"):
        return None
    m = OFFER_RE.match(text)
    if not m:
        return None
    left, right = Decimal(m.group(1)), Decimal(m.group(2))
    if left + right == 0:
        return None
    return left, right


def _has_value(raw) -> bool:
    text = str(_clean(raw))
    return text not in ("", "-", "0", "None")


RETURN_START_MARKERS = ("مر ",)
RETURN_TEXT_MARKERS = ("مرتجع", "مرد")


def is_return_invoice(invoice_text: str) -> bool:
    text = str(invoice_text or "").strip()
    if any(text.startswith(p) for p in RETURN_START_MARKERS):
        return True
    return any(marker in text for marker in RETURN_TEXT_MARKERS)


# ---------------------------------------------------------------------------
# قائمة الأسعار (دولار)
# ---------------------------------------------------------------------------

REQUIRED_PRICE_COLS = {"اسم المادة", "الكمية", "السعر"}


def parse_price_list(file_obj) -> dict:
    """يقرأ شيت 'جرد المواد' — يرجع dict بالأسماء الصالحة فقط (سعر > 0)،
    مع تجاهل الأسطر الدعائية (سعرها صفر، مثل الستاندات/البوسترات) وأسطر
    المجاميع الختامية بالأسفل."""
    import openpyxl

    wb = openpyxl.load_workbook(file_obj, data_only=True, read_only=True)
    sheet = None
    for name in wb.sheetnames:
        if "جرد المواد" in name or "اسعار" in name or "أسعار" in name:
            sheet = name
            break
    if sheet is None:
        sheet = wb.sheetnames[0]
    ws = wb[sheet]
    rows = list(ws.iter_rows(values_only=True))
    header_idx, cols = _find_header(rows, REQUIRED_PRICE_COLS)
    c_name, c_price = cols["اسم المادة"], cols["السعر"]

    prices: dict[str, Decimal] = {}
    zero_priced: list[str] = []
    for row in rows[header_idx + 1:]:
        if not row or row[c_name] in (None, "", 0):
            continue
        name = str(_clean(row[c_name]))
        if name in SUMMARY_ROW_LABELS or name.startswith("مجموع"):
            continue
        price = _to_decimal(row[c_price])
        if price <= 0:
            zero_priced.append(name)
            continue
        prices[name] = price
    return {"prices": prices, "zero_priced": zero_priced}


# ---------------------------------------------------------------------------
# دفتر الأستاذ — لمعرفة العملة/سعر الصرف الفعلي لكل فاتورة فقط
# ---------------------------------------------------------------------------

REQUIRED_LEDGER_COLS = {"أصل السند", "العملة الأصلية"}


def parse_currency_ledger(file_obj) -> dict:
    """يقرأ شيت 'دفتر الأستاذ' — يرجع dict[رقم الفاتورة] = قائمة
    (سعر الوحدة بالدولار, سعر الصرف المستخدَم) المُستخرَجة من عمود
    'العملة الأصلية' بصيغة '11.30 [$ 138.00]'. الأسطر بلا قيمة حقيقية
    بهذا العمود (0) تُتجاهَل — هي أسطر ليست دولارية."""
    import openpyxl

    wb = openpyxl.load_workbook(file_obj, data_only=True, read_only=True)
    sheet = None
    for name in wb.sheetnames:
        if "دفتر الأستاذ" in name or "استاذ" in name:
            sheet = name
            break
    if sheet is None:
        sheet = wb.sheetnames[0]
    ws = wb[sheet]
    rows = list(ws.iter_rows(values_only=True))
    header_idx, cols = _find_header(rows, REQUIRED_LEDGER_COLS)
    c_inv, c_cur = cols["أصل السند"], cols["العملة الأصلية"]

    out: dict[str, list] = {}
    parsed_count = 0
    unparsed_nonzero: list[str] = []
    for row in rows[header_idx + 1:]:
        if not row:
            continue
        cur_raw = row[c_cur]
        if cur_raw in (None, "", 0, "0"):
            continue
        m = CURRENCY_CELL_RE.match(str(cur_raw).strip())
        if not m:
            unparsed_nonzero.append(str(cur_raw))
            continue
        usd_price = _to_decimal(m.group(1))
        rate = _to_decimal(m.group(2))
        inv = str(_clean(row[c_inv]))
        out.setdefault(inv, []).append((usd_price, rate))
        parsed_count += 1
    return {"by_invoice": out, "parsed_count": parsed_count, "unparsed_nonzero": unparsed_nonzero}


# ---------------------------------------------------------------------------
# الحركة اليومية (مفرق) — بيع ومرتجع الارجيفيت بالليرة
# ---------------------------------------------------------------------------

REQUIRED_MOVEMENT_COLS = {"الفاتورة", "التاريخ", "اسم الزبون", "اسم المادة", "كمية", "الهدايا", "الإفرادي", "السعر الإجمالي"}


@dataclass
class ArgivitRow:
    row_no: int
    invoice: str
    date: str
    customer: str
    item: str
    retail_offer: str
    special_offer1: str
    special_offer: str
    qty: Decimal
    gifts: Decimal
    unit_price: Decimal        # الإفرادي
    total_price: Decimal       # السعر الإجمالي
    discount: Decimal          # الحسم
    gift_discount: Decimal     # حسم هدايا
    is_return: bool = False
    is_dollar: Optional[bool] = None
    dollar_rate: Optional[Decimal] = None
    dollar_usd_price: Optional[Decimal] = None
    dollar_note: str = ""


def parse_daily_movement(file_obj) -> list:
    """يقرأ شيت 'الحركة اليومية' مع تعبئة تنازلية (forward-fill) لأعمدة
    الفاتورة والتاريخ واسم الزبون الثلاثة معاً عند 0/فراغ (نفس روح
    الخطوة 1 بوحدة فيتا فارما، موسَّعة لثلاثة أعمدة بدل عمود واحد، لأن
    هذا الملف يُفرِّغ الثلاثة معاً لأسطر المادة الثانية فما بعد بنفس
    الفاتورة)."""
    import openpyxl

    wb = openpyxl.load_workbook(file_obj, data_only=True, read_only=True)
    sheet = None
    for name in wb.sheetnames:
        if "الحركة اليومية" in name or "حركة يومية" in name:
            sheet = name
            break
    if sheet is None:
        sheet = wb.sheetnames[0]
    ws = wb[sheet]
    rows = list(ws.iter_rows(values_only=True))
    header_idx, cols = _find_header(rows, REQUIRED_MOVEMENT_COLS)

    c_inv, c_date, c_cust, c_item = cols["الفاتورة"], cols["التاريخ"], cols["اسم الزبون"], cols["اسم المادة"]
    c_retail, c_sp1, c_sp = cols.get("عرض المفرق"), cols.get("عرض مميز1"), cols.get("عرض مميز")
    c_qty, c_gifts = cols["كمية"], cols["الهدايا"]
    c_unit, c_total = cols["الإفرادي"], cols["السعر الإجمالي"]
    c_disc, c_gdisc = cols.get("الحسم"), cols.get("حسم هدايا")

    out: list[ArgivitRow] = []
    last_inv, last_date, last_cust = "", "", ""
    for i, row in enumerate(rows[header_idx + 1:]):
        if not row:
            continue
        # صف عناوين ثانٍ ("الفاتورة" حرفياً بعمود الفاتورة) يُشير دائماً إلى
        # بدء قسم تذييل/مجاميع ختامية (مثل "مرتجع مبيعات دولار"/"مبيعات
        # دولار"/"الإجمالي") — نتوقف هنا كلياً، لأن هذا القسم ليس حركة
        # فعلية وقد يحمل بعمود "اسم المادة" نصاً مثل "مجموع الآجل" يمرّ
        # من فلتر "اسم مادة غير فارغ" لو لم نتوقف صريحاً.
        if str(_clean(row[c_inv])) == "الفاتورة":
            break
        if row[c_item] in (None, ""):
            continue
        raw_inv = _clean(row[c_inv])
        if raw_inv in (None, "", 0, "0"):
            inv_text, date_text, cust_text = last_inv, last_date, last_cust
        else:
            inv_text = str(raw_inv)
            date_text = str(_clean(row[c_date]))
            cust_text = str(_clean(row[c_cust]))
            last_inv, last_date, last_cust = inv_text, date_text, cust_text

        out.append(ArgivitRow(
            row_no=i,
            invoice=inv_text, date=date_text, customer=cust_text,
            item=str(_clean(row[c_item])),
            retail_offer=str(_clean(row[c_retail])) if c_retail is not None else "-",
            special_offer1=str(_clean(row[c_sp1])) if c_sp1 is not None else "-",
            special_offer=str(_clean(row[c_sp])) if c_sp is not None else "-",
            qty=_to_decimal(row[c_qty]), gifts=_to_decimal(row[c_gifts]),
            unit_price=_to_decimal(row[c_unit]), total_price=_to_decimal(row[c_total]),
            discount=_to_decimal(row[c_disc]) if c_disc is not None else Decimal("0"),
            gift_discount=_to_decimal(row[c_gdisc]) if c_gdisc is not None else Decimal("0"),
            is_return=is_return_invoice(inv_text),
        ))
    return out


def apply_dollar_flags(rows: list, ledger: dict, prices: dict) -> None:
    """يُسنِد لكل سطر: هل فاتورته دولارية أصلاً، وبأي سعر صرف — بالاعتماد
    حصراً على دفتر الأستاذ (حقل 'مواد دولار'، حسب تأكيد المستخدم أن
    دوره الوحيد هنا هو معرفة نوع العملة، لا أكثر).

    **ملاحظة فنية مهمة (اكتُشفت أثناء التحقق الرقمي 2026-10-01):** عمود
    'العملة الأصلية' بدفتر الأستاذ لا يحمل سعر مادة واحدة بالضرورة، بل
    أحياناً **مجموع أسعار عدة مواد مجمَّعة بقيد محاسبي واحد** لنفس
    الفاتورة (تحقّق فعلي: قيد بسعر "24.50 [$ 133.00]" على فاتورة تحوي
    مادتين سعرهما بالقائمة 13.2 و11.3 — ومجموعهما 24.5 بالضبط). لذلك لا
    يصحّ مطابقة السعر الدولاري لكل سطر/مادة على حدة (تُعطي "غير مؤكَّد"
    لأغلب الأسطر زوراً)، بل يكفي — وهو ما طلبه المستخدم فعلاً — اعتبار
    **كل أسطر الفاتورة دولارية إن وُجد لها أي قيد دولاري بدفتر الأستاذ
    مهما كان تفصيله**، مع عرض سعر (أسعار) الصرف الفعلي المرصود لنفس
    الفاتورة للمرجعية فقط."""
    by_invoice = ledger.get("by_invoice", {})
    for r in rows:
        candidates = by_invoice.get(r.invoice, [])
        if not candidates:
            r.is_dollar = False
            r.dollar_note = "لا يوجد أي قيد دولاري بنفس رقم هذه الفاتورة بدفتر الأستاذ"
            continue
        rates = sorted({rate for _, rate in candidates})
        r.is_dollar = True
        r.dollar_rate = rates[0] if len(rates) == 1 else None
        r.dollar_note = f"دولاري — سعر الصرف المرصود بدفتر الأستاذ لهذه الفاتورة: {', '.join(str(x) for x in rates)}"


# ---------------------------------------------------------------------------
# مراحل مطابقة السعر الافرادي (المرحلة 1-5)
# ---------------------------------------------------------------------------

@dataclass
class ExchangeRateRange:
    lo: Decimal
    hi: Decimal

    @classmethod
    def fixed(cls, rate):
        r = _to_decimal(rate)
        return cls(lo=r, hi=r)

    @classmethod
    def ranged(cls, lo, hi):
        return cls(lo=_to_decimal(lo), hi=_to_decimal(hi))


ROUNDING_TOLERANCE = Decimal("1")  # ليرة واحدة سماحية تقريب فوق/تحت النطاق


def _in_range(value: Decimal, lo: Decimal, hi: Decimal) -> bool:
    return (lo - ROUNDING_TOLERANCE) <= value <= (hi + ROUNDING_TOLERANCE)


@dataclass
class PriceMatchRow:
    row: ArgivitRow
    tier: str
    expected_lo: Decimal
    expected_hi: Decimal
    actual_value: Decimal
    basis: str   # شرح أساس المقارنة (الإفرادي مباشرة / بعد خصم الحسم / بنسبة العرض)
    note: str = ""


def _price_for(item: str, prices: dict) -> Optional[Decimal]:
    return prices.get(item)


def match_tier1_direct(rows, prices, rate_range):
    matched, remaining = [], []
    for r in rows:
        price = _price_for(r.item, prices)
        if price is None:
            remaining.append(r)
            continue
        lo, hi = price * rate_range.lo, price * rate_range.hi
        if r.unit_price > 0 and _in_range(r.unit_price, lo, hi):
            matched.append(PriceMatchRow(row=r, tier="مطابقين", expected_lo=lo, expected_hi=hi,
                                          actual_value=r.unit_price, basis="الإفرادي مباشرة"))
        else:
            remaining.append(r)
    return matched, remaining


def match_tier2_after_discount(rows, prices, rate_range):
    matched, remaining = [], []
    for r in rows:
        price = _price_for(r.item, prices)
        if price is None or r.qty <= 0 or r.discount <= 0:
            remaining.append(r)
            continue
        effective_unit = ((r.total_price - r.discount) / r.qty).quantize(Decimal("0.01"))
        lo, hi = price * rate_range.lo, price * rate_range.hi
        if _in_range(effective_unit, lo, hi):
            matched.append(PriceMatchRow(row=r, tier="مطابقين بعد خصم الحسم", expected_lo=lo, expected_hi=hi,
                                          actual_value=effective_unit,
                                          basis="(السعر الإجمالي − الحسم) ÷ الكمية"))
        else:
            remaining.append(r)
    return matched, remaining


def match_tier_offer(rows, prices, rate_range, offer_field: str, tier_label: str):
    matched, remaining = [], []
    for r in rows:
        price = _price_for(r.item, prices)
        offer_raw = getattr(r, offer_field)
        lr = parse_offer_lr(offer_raw)
        if price is None or lr is None or r.unit_price <= 0:
            remaining.append(r)
            continue
        left, right = lr
        ratio = left / (left + right)
        expected_unit = price * ratio
        lo, hi = expected_unit * rate_range.lo, expected_unit * rate_range.hi
        if _in_range(r.unit_price, lo, hi):
            matched.append(PriceMatchRow(
                row=r, tier=tier_label, expected_lo=lo, expected_hi=hi, actual_value=r.unit_price,
                basis=f"السعر × ({left}÷{left+right}) [{offer_field} = {offer_raw}]",
            ))
        else:
            remaining.append(r)
    return matched, remaining


def compute_vita_compliance(rows: list) -> dict:
    """يُشغِّل فحص "فيتا فارما" (compensation/engine.py) حرفياً بلا أي
    تعديل على منطقه، على كل أسطر الحركة التي تملك عرضاً مميزاً فعلياً،
    ليُستخدَم كتحقّق إضافي منفصل (التزام الكميات/الهدايا بالعروض) — لا
    يؤثر على قرار مطابقة السعر بأي تيرة. يرجع dict[(مادة, عرض مفرق)] =
    قيمة المطالبة الصافية (0 = ملتزم تماماً، غير 0 = انحراف بالهدايا)."""
    vita_rows = [
        VitaMovementRow(
            invoice=r.invoice, date=r.date, customer=r.customer, item=r.item,
            retail_offer=r.retail_offer, special_offer1=r.special_offer1, special_offer=r.special_offer,
            qty=r.qty, gifts=r.gifts, is_return=r.is_return, is_excluded_type=False,
        )
        for r in rows
    ]
    offer_rows = [r for r in vita_rows if vita_has_special_offer(r)]
    groups = vita_compute_claim_groups(offer_rows)
    return {(g.item, g.retail_offer): g for g in groups}


@dataclass
class PriceMatchResult:
    tier1: list
    tier2: list
    tier3_retail: list
    tier4_special: list
    unmatched: list
    vita_compliance: dict


def run_price_matching(movement_rows: list, prices: dict, rate_range: ExchangeRateRange) -> PriceMatchResult:
    sale_rows = [r for r in movement_rows]  # المراحل تُطبَّق على كل الأسطر (بيع ومرتجع) على حد سواء
    tier1, rest = match_tier1_direct(sale_rows, prices, rate_range)
    tier2, rest = match_tier2_after_discount(rest, prices, rate_range)
    tier3, rest = match_tier_offer(rest, prices, rate_range, "retail_offer", "مطابق على العرض المفرق")
    tier4a, rest = match_tier_offer(rest, prices, rate_range, "special_offer1", "مطابق على العرض المميز")
    tier4b, rest = match_tier_offer(rest, prices, rate_range, "special_offer", "مطابق على العرض المميز")
    tier4 = tier4a + tier4b
    vita_compliance = compute_vita_compliance(movement_rows)
    return PriceMatchResult(tier1=tier1, tier2=tier2, tier3_retail=tier3, tier4_special=tier4,
                             unmatched=rest, vita_compliance=vita_compliance)


# ---------------------------------------------------------------------------
# مطابقة المبيعات مع المرتجعات حسب الزبون (مفرق)
# ---------------------------------------------------------------------------

@dataclass
class CustomerReconciliationGroup:
    customer: str
    item: str
    sale_rows: list
    return_rows: list
    reasons: list = field(default_factory=list)
    matched: bool = False


def reconcile_retail_sales_returns(movement_rows: list) -> dict:
    """تُقسَّم النتيجة لثلاث قوائم، لا قائمتين — تمييز مهم: أغلب أسطر
    البيع لا تملك أي مرتجع بنفس الشهر أصلاً (طبيعي تماماً، وليس خللاً)،
    فلا يصحّ عدّها "غير مطابقة" مع الحالات التي فيها بيع ومرتجع فعلاً
    لكن سعرهما/حسمهما/عملتهما تختلف (هذه فقط المشكلة الحقيقية):
    - matched: بيع ومرتجع معاً، وكل الفحوص الثلاثة تطابقت.
    - mismatched: بيع ومرتجع معاً، لكن فحصاً واحداً أو أكثر لم يتطابق.
    - no_counterpart: طرف واحد فقط موجود (بيع بلا مرتجع أو العكس) — لا
      يوجد ما يُقارَن أصلاً، فلا يُعتبر "خطأ" بل معلومة فقط."""
    groups: dict[tuple, CustomerReconciliationGroup] = {}
    for r in movement_rows:
        key = (r.customer, r.item)
        g = groups.setdefault(key, CustomerReconciliationGroup(customer=r.customer, item=r.item, sale_rows=[], return_rows=[]))
        (g.return_rows if r.is_return else g.sale_rows).append(r)

    matched, mismatched, no_counterpart = [], [], []
    for g in groups.values():
        if not g.sale_rows and not g.return_rows:
            continue
        if not g.sale_rows or not g.return_rows:
            g.reasons.append("لا يوجد طرف مقابل لهذا الزبون/المادة ضمن هذا الملف (بيع بلا مرتجع أو العكس)")
            no_counterpart.append(g)
            continue

        sale_prices = {s.unit_price.quantize(Decimal("0.01")) for s in g.sale_rows if s.unit_price}
        return_prices = {s.unit_price.quantize(Decimal("0.01")) for s in g.return_rows if s.unit_price}
        if not return_prices.issubset(sale_prices):
            g.reasons.append(f"السعر غير مطابق: أسعار المرتجع {sorted(return_prices)} لا تطابق أسعار المبيع {sorted(sale_prices)}")

        def _disc_ratio(row):
            if row.total_price:
                return (row.discount / row.total_price).quantize(Decimal("0.0001"))
            return Decimal("0")
        sale_disc = {_disc_ratio(s) for s in g.sale_rows}
        return_disc = {_disc_ratio(s) for s in g.return_rows}
        if not return_disc.issubset(sale_disc):
            g.reasons.append(f"الحسم غير مطابق: نسب حسم المرتجع {sorted(return_disc)} لا تطابق نسب حسم المبيع {sorted(sale_disc)}")

        # فحص العملة: يُستثنى is_dollar=None (غير مؤكَّد — لا قيد مطابق
        # بدفتر الأستاذ) من المقارنة، لأنه "لا نعلم" وليس "قيمة مختلفة"؛
        # يُعتبر خللاً فعلياً فقط حين يملك الطرفان قيمة مؤكَّدة (True/False)
        # ومختلفة فعلاً.
        sale_confirmed = {s.is_dollar for s in g.sale_rows if s.is_dollar is not None}
        return_confirmed = {s.is_dollar for s in g.return_rows if s.is_dollar is not None}
        if sale_confirmed and return_confirmed and sale_confirmed != return_confirmed:
            g.reasons.append(f"العملة غير مطابقة: حالة الدولرة المؤكَّدة بالمبيع {sale_confirmed} تختلف عن المرتجع {return_confirmed}")

        if g.reasons:
            mismatched.append(g)
        else:
            g.matched = True
            matched.append(g)

    return {"matched": matched, "mismatched": mismatched, "no_counterpart": no_counterpart}


# ---------------------------------------------------------------------------
# مطابقة بيع/مرتجع الجملة (ملف منفصل، عام لكل المواد)
# ---------------------------------------------------------------------------

REQUIRED_WHOLESALE_COLS = REQUIRED_MOVEMENT_COLS


@dataclass
class WholesaleRow:
    invoice: str
    date: str
    customer: str
    item: str
    qty: Decimal
    gifts: Decimal
    unit_price: Decimal
    total_price: Decimal
    discount: Decimal
    is_return: bool = False


def _normalize_prefix(invoice_text: str) -> str:
    return (invoice_text or "").split(":")[0].replace(" ", "").strip()


def is_wholesale_return(invoice_text: str) -> bool:
    return _normalize_prefix(invoice_text).startswith("م.مبيع")


def is_wholesale_sale(invoice_text: str) -> bool:
    return _normalize_prefix(invoice_text).startswith("ع.مبيع")


def parse_wholesale_movement(file_obj) -> list:
    """يقرأ ملف 'مبيعات جملة مع المرتجعات' — نفس بنية شيت الحركة اليومية
    لكنه عام (كل المواد لا الارجيفيت فقط)، وبوادئ فواتير مختلفة
    (ع.مبيع ج للبيع، م.مبيع ج للمرتجع — بتطبيع المسافات حول النقطة)."""
    import openpyxl

    wb = openpyxl.load_workbook(file_obj, data_only=True, read_only=True)
    sheet = None
    for name in wb.sheetnames:
        if "الحركة اليومية" in name or "حركة يومية" in name or "جملة" in name:
            sheet = name
            break
    if sheet is None:
        sheet = wb.sheetnames[0]
    ws = wb[sheet]
    rows = list(ws.iter_rows(values_only=True))
    header_idx, cols = _find_header(rows, REQUIRED_WHOLESALE_COLS)

    c_inv, c_date, c_cust, c_item = cols["الفاتورة"], cols["التاريخ"], cols["اسم الزبون"], cols["اسم المادة"]
    c_qty, c_gifts = cols["كمية"], cols["الهدايا"]
    c_unit, c_total = cols["الإفرادي"], cols["السعر الإجمالي"]
    c_disc = cols.get("الحسم")

    out: list[WholesaleRow] = []
    last_inv, last_date, last_cust = "", "", ""
    for row in rows[header_idx + 1:]:
        if not row:
            continue
        if str(_clean(row[c_inv])) == "الفاتورة":
            break  # بداية قسم التذييل/المجاميع الختامية — انظر نفس الملاحظة بـparse_daily_movement
        if row[c_item] in (None, ""):
            continue
        raw_inv = _clean(row[c_inv])
        if raw_inv in (None, "", 0, "0"):
            inv_text, date_text, cust_text = last_inv, last_date, last_cust
        else:
            inv_text = str(raw_inv)
            date_text = str(_clean(row[c_date]))
            cust_text = str(_clean(row[c_cust]))
            last_inv, last_date, last_cust = inv_text, date_text, cust_text

        out.append(WholesaleRow(
            invoice=inv_text, date=date_text, customer=cust_text, item=str(_clean(row[c_item])),
            qty=_to_decimal(row[c_qty]), gifts=_to_decimal(row[c_gifts]),
            unit_price=_to_decimal(row[c_unit]), total_price=_to_decimal(row[c_total]),
            discount=_to_decimal(row[c_disc]) if c_disc is not None else Decimal("0"),
            is_return=is_wholesale_return(inv_text),
        ))
    return out


@dataclass
class WholesaleReconciliationGroup:
    customer: str
    item: str
    sale_rows: list
    return_rows: list
    reasons: list = field(default_factory=list)
    matched: bool = False


def reconcile_wholesale_sales_returns(rows: list) -> dict:
    groups: dict[tuple, WholesaleReconciliationGroup] = {}
    for r in rows:
        if not (is_wholesale_sale(r.invoice) or is_wholesale_return(r.invoice)):
            continue
        key = (r.customer, r.item)
        g = groups.setdefault(key, WholesaleReconciliationGroup(customer=r.customer, item=r.item, sale_rows=[], return_rows=[]))
        (g.return_rows if r.is_return else g.sale_rows).append(r)

    matched, mismatched, no_counterpart = [], [], []
    for g in groups.values():
        if not g.sale_rows and not g.return_rows:
            continue
        if not g.sale_rows or not g.return_rows:
            g.reasons.append("لا يوجد طرف مقابل لهذا الزبون/المادة ضمن هذا الملف (بيع بلا مرتجع أو العكس)")
            no_counterpart.append(g)
            continue

        sale_qtys = {s.qty for s in g.sale_rows}
        return_qtys = {s.qty for s in g.return_rows}
        if not return_qtys.issubset(sale_qtys):
            g.reasons.append(f"الكمية غير مطابقة: كميات المرتجع {sorted(return_qtys)} لا تطابق كميات المبيع {sorted(sale_qtys)}")

        def _disc_ratio(row):
            if row.total_price:
                return (row.discount / row.total_price).quantize(Decimal("0.0001"))
            return Decimal("0")
        sale_disc = {_disc_ratio(s) for s in g.sale_rows}
        return_disc = {_disc_ratio(s) for s in g.return_rows}
        if not return_disc.issubset(sale_disc):
            g.reasons.append(f"نسبة الحسم غير مطابقة: نسب المرتجع {sorted(return_disc)} لا تطابق نسب المبيع {sorted(sale_disc)}")

        if g.reasons:
            mismatched.append(g)
        else:
            g.matched = True
            matched.append(g)

    return {"matched": matched, "mismatched": mismatched, "no_counterpart": no_counterpart}


# ---------------------------------------------------------------------------
# التجميع العام
# ---------------------------------------------------------------------------

def build_result(movement_file, price_file, ledger_file, rate_range: ExchangeRateRange, wholesale_file=None) -> dict:
    price_data = parse_price_list(price_file)
    ledger_data = parse_currency_ledger(ledger_file)
    movement_rows = parse_daily_movement(movement_file)
    apply_dollar_flags(movement_rows, ledger_data, price_data["prices"])

    price_match = run_price_matching(movement_rows, price_data["prices"], rate_range)
    retail_reconciliation = reconcile_retail_sales_returns(movement_rows)

    wholesale_rows, wholesale_reconciliation = None, None
    if wholesale_file is not None:
        wholesale_rows = parse_wholesale_movement(wholesale_file)
        wholesale_reconciliation = reconcile_wholesale_sales_returns(wholesale_rows)

    return {
        "price_data": price_data,
        "ledger_data": ledger_data,
        "movement_rows": movement_rows,
        "price_match": price_match,
        "retail_reconciliation": retail_reconciliation,
        "wholesale_rows": wholesale_rows,
        "wholesale_reconciliation": wholesale_reconciliation,
        "rate_range": rate_range,
        "summary": {
            "movement_rows_count": len(movement_rows),
            "tier1_count": len(price_match.tier1),
            "tier2_count": len(price_match.tier2),
            "tier3_count": len(price_match.tier3_retail),
            "tier4_count": len(price_match.tier4_special),
            "unmatched_count": len(price_match.unmatched),
            "retail_matched_count": len(retail_reconciliation["matched"]),
            "retail_mismatched_count": len(retail_reconciliation["mismatched"]),
            "retail_no_counterpart_count": len(retail_reconciliation["no_counterpart"]),
            "wholesale_matched_count": len(wholesale_reconciliation["matched"]) if wholesale_reconciliation else 0,
            "wholesale_mismatched_count": len(wholesale_reconciliation["mismatched"]) if wholesale_reconciliation else 0,
            "wholesale_no_counterpart_count": len(wholesale_reconciliation["no_counterpart"]) if wholesale_reconciliation else 0,
        },
    }
