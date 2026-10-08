"""
منطق معالجة تعويضات فيتا فارما — إعادة بناء ثانية بطلب المستخدم الصريح
بتاريخ 2026-08-31 (بعد الإعادة الأولى بتاريخ 2026-08-30 والتصحيحات
الأولى بتاريخ 2026-08-31 المبنية على ملف مرجعي "فيتا شهر 8"). هذه
النسخة تُطبَّق **على مستوى كل سطر بمفرده** (وليس على مستوى مجموعة
مجمَّعة)، وتُسقط الزبون من مفتاح التجميع بالكامل، بناءً على شرح
تفصيلي ثانٍ زوّدنا به المستخدم بالعامية خطوة بخطوة.

**تعديل ثالث (2026-08-31، بالصور):** أضيفت خطوة "دمج أسطر الكمية=صفر"
(انظر merge_zero_qty_rows أدناه) — قبل تطبيق المعادلة على كل سطر، أي
سطر كميته صفر (لكن هداياه فعلية) يُدمَج مع سطر آخر **لنفس الزبون**
ضمن نفس الحزمة (مادة × عرض مفرق) بإضافة هداياه إليه، ثم يُحذف سطر
الكمية=صفر بالكامل. هذا يمنع معاملة سطر الكمية=صفر كسطر مستقل بناتج
معادلة = صفر (كان سيُعطى صافياً = هداياه الكاملة كـ"ربح مجاني" غير
صحيح). تحقّق بمثال حقيقي زوّدنا به المستخدم بالصور: فاتورة كمية=0
هدايا=5 لصيدلية "الزعيم - ساحة شمدين" دُمجت مع فاتورة أخرى لنفس
الصيدلية (كمية=10 هدايا=6) لتصبح كمية=10 هدايا=11 — مطابق تماماً.

خطوات المعالجة الجديدة (بالترتيب الحرفي الذي وصفه المستخدم 2026-08-31):

 1. تعبئة رقم الفاتورة: كل قيمة 0 (أو فارغة) في عمود "الفاتورة" تُستبدل
    برقم فاتورة السطر الذي قبلها مباشرة (forward-fill) — لم يتغيّر.

 2. فلترة العروض المميزة: يبقى فقط السطور التي تملك "عرض مميز" فعلي
    (عمود "عرض مميز1" أو "عرض مميز" غير فارغ/"-"/"0"). أي مادة لا تملك
    أي سطر بعرض مميز في كل الملف تُستبعد تلقائياً بالكامل — لم يتغيّر.

 3. اختيار مادة، ثم فلترة على قيمة "عرض المفرق" ضمن هذه المادة (قد
    يكون لمادة واحدة أكثر من عرض مفرق) — أي مستوى التجميع الآن هو
    (مادة × عرض مفرق) فقط.

 4. **تغيير جوهري 2026-08-31: تُهمَل الفلترة/التجميع على اسم الصيدلية
    (الزبون) كلياً.** كل الأسطر ضمن (مادة × عرض مفرق) تُعالَج معاً بلا
    أي اعتبار لاسم الزبون — سواء بالتجميع النهائي أو بمطابقة أزواج
    الإلغاء بالخطوة التالية. هذا تصحيح صريح من المستخدم: "للدقة رح
    نهمل الفلترة على اسم الصيدلية".

 5. إلغاء أزواج المرتجع/المبيع المتطابقة، ضمن نطاق (مادة × عرض مفرق)
    فقط، وبمطابقة **الكمية والهدايا حصراً (بلا اشتراط نفس الزبون)**:
    - فواتير "م. مبيع" (تصحيحات/سحوبات مبيعات، رقم الفاتورة يبدأ بـ
      "م.") تُطابَق مع أي سطر بيع آخر (رقم فاتورة يبدأ بـ"ع") بنفس
      الكمية والهدايا ضمن نفس الحزمة (مادة × عرض مفرق) — إن وُجد
      يُحذف الاثنان معاً؛ وإلا يُحذف سطر "م. مبيع" وحده.
    - فواتير المرتجعات الصريحة ("مرتجع"/"مرد" في نص الفاتورة) تُطابَق
      بنفس الطريقة (كمية وهدايا فقط، بلا زبون)؛ المرتجع بلا مطابقة
      يبقى ضمن البيانات ويُعلَّم للمراجعة (لا يُستبعد بمفرده).
    بادئة "مسحوب" مختلفة تماماً وتبقى محتسبة بشكل طبيعي (لم تتغيّر).

 6. **تغيير جوهري 2026-08-31: تُطبَّق المعادلة على مستوى كل سطر
    بمفرده** (وليس على كمية مجمَّعة كما في النسخة السابقة): لكل سطر
    باقٍ ضمن الحزمة — ناتج معادلة السطر = كمية السطر × (الرقم الأصغر
    في عرض المفرق ÷ الرقم الأكبر فيه). ثم صافي السطر = هدايا السطر −
    ناتج معادلة السطر.
    تحقّق رقمي مباشر (2026-08-31) مقابل عمود "الإفرادي" الحقيقي بملف
    "فيتا شهر 8": القيمة مطابقة تماماً سطراً بسطر (مثال: كمية 100 مع
    عرض "10+5" → 50 بالضبط؛ كمية 7 مع عرض "10+4" → 2.8 بالضبط).

 7. **تغيير جوهري 2026-08-31: كل سطر يكون صافيه (هدايا − ناتج المعادلة)
    سالباً أو صفراً يُحذف بالكامل** من الحساب — لا كميته ولا هداياه
    ولا ناتج معادلته يدخل أي مجموع لاحق. هذا تصحيح صريح من المستخدم
    ("السوالب اللي رح يطلعو عنا والصفار بالنتيجة لازم نحذف اسطرن
    بالكامل") — طُبِّق حرفياً كما طلب رغم وجود تعارض جزئي مع الدليل
    الأقوى (انظر "ملاحظة تحقّق مهمة" أدناه)، لأن المستخدم أكّد صراحةً
    اعتماد هذه القاعدة بعد أن عُرِض عليه التعارض بالأرقام.

 8. تُجمع كمية وهدايا وناتج معادلة **الأسطر الباقية فقط** (بعد حذف
    السالب/الصفر بالخطوة 7) لكل حزمة (مادة × عرض مفرق):
    - مجموع الكمية، مجموع الهدايا، مجموع ناتج المعادلة.
    - المطالبة النهائية للحزمة = مجموع الهدايا − مجموع ناتج المعادلة
      (يساوي رياضياً مجموع "صافي" الأسطر الموجَبة فقط).

 9. تُكرَّر الخطوات 3-8 لكل قيمة "عرض مفرق" مختلفة ضمن نفس المادة، ولكل
    مادة على حدة. النتيجة النهائية تُعرض على مستوى (مادة × عرض مفرق) —
    **بلا تفصيل لكل زبون بمستوى المجموع** (رغم أن كل سطر أصلي يبقى
    ظاهراً بالكامل في شيت المادة التفصيلي للتدقيق، مع عمود الزبون
    الأصلي للمرجعية فقط — لا يدخل الزبون في أي حساب).

**تعديل رابع (2026-09-26، بطلب المستخدم الصريح):** الخطوة 3 القديمة (أعلاه،
"إن لم توجد قيمة 'عرض مفرق' صالحة لحزمة ما... تظهر كاملة... بمطالبة فارغة")
تغيّرت جذرياً. رسالة المستخدم: "هناك عروض مميزة لا يوجد لها عرض مفرق أحتاج
منك أن بهذه الحالة أن تجمع كل الهدايا للمادة في حال وجود عرض مميز لها."
أي: حزمة (مادة × عرض مفرق) اجتازت فلتر "عرض مميز فعلي" (الخطوة 2) لكن قيمة
"عرض مفرق" لديها غير صالحة/مفهومة — مطالبتها الآن = **مجموع كل هدايا أسطر
الحزمة مباشرة** (بعد إلغاء أزواج "م. مبيع"/المرتجعات ودمج أسطر الكمية=صفر
كالمعتاد)، بلا أي طرح لناتج معادلة (لا توجد نسبة عرض مفرق لحسابها أصلاً)،
بدل تركها فارغة بانتظار مراجعة يدوية. راجع compute_bucket أدناه (فرع
`retail is None`). لا يوجد مفهوم "صافي سالب/صفري" لهذه الحزم (لا معادلة
تُطرح)، فكل أسطرها تُعتبر مُدرَجة بالكامل بالمجموع.

ملاحظة تحقّق مهمة (تعارض مكتشَف 2026-08-31، عُرِض على المستخدم وأكّد
اعتماد القاعدة الحرفية رغم ذلك):
  عند تطبيق كل الخطوات أعلاه على ملف "فيتا شهر 8" الحقيقي، مادة "اوستيو
  فيكس 30 حبة" تُعطي **883.50 بالضبط** إن لم تُحذف الأسطر ذات الصافي
  السالب/الصفري (مطابقة تامة 100% لصيغة =SUM(K2:K145) الحية الموجودة
  فعلياً في الملف المرجعي — أقوى دليل ممكن). أما بتطبيق حذف السالب/
  الصفر كما وصفه المستخدم فتُعطي **899.00** (فرق +15.5). عُرِض هذا
  التعارض على المستخدم صراحة بالأرقام، وأكّد اعتماد قاعدة "حذف السالب
  والصفر" رغم ذلك — فطُبِّقت هنا حرفياً. الاحتمال الأرجح: ملف "اوستيو
  فيكس" المرجعي نفسه لم تُطبَّق عليه هذه القاعدة يدوياً بشكل متسق (رغم
  أن مادة "باراماكس" المرجعية تدعم القاعدة: مجموع الأسطر الموجبة فقط
  فيها يطابق قيمتها المرجعية 1280 تماماً، بعكس مجموع كل الأسطر الذي
  يعطي 1277.4). يُنصَح بمراجعة هذه النقطة يدوياً إن ظهر فرق غير متوقع
  مستقبلاً على مواد أخرى.

**تعديل خامس (2026-10-04، بطلب المستخدم الصريح بعد تدقيق حالة حقيقية):**
اكتُشف أثناء مطابقة نتائج النظام مع ملف "مطالبة" يدوي مرجعي أن مادة
"غلوبيفيت كبير شراب 200 مل" أعطت 375 بدل 325 (فرق +50). التدقيق سطراً
بسطر كشف السبب: فاتورة "م. مبيع ج: 27" لـ"مستودع بركات- دمشق" بكمية
100 وهدايا 80 (تصحيح/سحب مبيعات جملة) — لا يوجد لها سطر بيع واحد بنفس
الكمية والهدايا بالضبط لتُلغى معه (أقصى كمية بسطر بيع فردي هنا 20)،
فكانت تُستبعد بمفردها بلا أي أثر على المجموع (كما صُمم `cancel_mabee_pairs`
أصلاً)، تاركةً 8 فواتير بيع صغيرة (موجودة فعلاً وصحيحة) مُدرَجة بالكامل
بالمجموع رغم أنها بالواقع تمثّل نفس الكمية التي صُحِّحت/أُعيدت.

شرح المستخدم الحرفي لآلية فريق المالية الفعلية: "الفاتورة مرتجع مبيع
ضمن مستودع بركات هية طلعت 100+80 اضطرينا نجمع من فواتير المبيعات...
لحتى يطلع معنا 100+80" — أي أن المالية تطابق تصحيح/مرتجع كبير الحجم
مع **تجميع عدة فواتير بيع أصغر** (لا فاتورة واحدة) يكون مجموع كمياتها
ومجموع هداياها معاً (الشرطان بآن واحد) يطابق تماماً كمية وهدايا سطر
التصحيح/المرتجع، ثم تُلغي الكل معاً. أكّد المستخدم أيضاً أنه "لا يوجد
كسر عملياً" (أي لا حاجة لمعالجة باقي كسري عند عدم وجود مطابقة تامة
لمضاعفات 100 — الحالة غير متوقعة عملياً، وتبقى الفاتورة بلا مطابقة
كالسابق إن لم توجد مطابقة تامة).

التطبيق: أُضيفت `_find_pool_match` (بحث DP/تراجعي مجمَّع حسب القيم
المتكررة، يُفضَّل أقل عدد أسطر ممكن) تُستخدَم تلقائياً داخل
`_cancel_pairs_by_qty_gifts` لكل من "م. مبيع" والمرتجعات: إن لم توجد
مطابقة مباشرة (سطر واحد)، يُحاوَل إيجاد تجميع عدة فواتير بيع يطابق
تماماً قبل اعتبار السطر "بلا مطابقة". التحقق العكسي بمثال "غلوبيفيت
كبير" الحقيقي: مجموعة من 7 من الفواتير الثمانية (4 بكمية 10/هدايا 8 +
3 بكمية 20/هدايا 16 = كمية 100 وهدايا 80 بالضبط) أُلغيت تلقائياً مع
فاتورة "م. مبيع ج: 27"، فانخفضت مطالبة المادة من 375 إلى **325 بالضبط**
— مطابقة تامة للمرجع اليدوي. الفاتورة الثامنة المتبقية بقيت مُدرَجة
بشكل طبيعي (لم تكن جزءاً من أي تجميع). كل مطابقة تجميع تُسجَّل وتظهر
بشيت تصدير مخصص للتدقيق (`result["pool_matches"]`) — راجع
compensation/excel_export.py.

تغييرات محفوظة من النسخة السابقة (2026-08-30/31) دون تعديل:
  - تعبئة رقم الفاتورة الصفري من السطر السابق (الخطوة 1).
  - فلترة "عرض مميز مفرق فقط" (الخطوة 2) — عمودا "عرض مميز"/"عرض مميز1"
    لا يدخلان بالحساب، فقط شرط أهلية.
  - استبعاد "م. مبيع" دائماً (مع محاولة مطابقة أولاً) — الخطوة 5.
  - بادئة "مسحوب" محتسبة بشكل طبيعي دائماً.
  - إن لم توجد قيمة "عرض مفرق" صالحة لحزمة ما، لا يمكن تطبيق المعادلة
    عليها — تظهر كاملة (بكميتها وهداياها الخام) في شيت مستقل للمراجعة
    اليدوية، بمطالبة فارغة، بدل أي افتراض ضمني.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from typing import Optional

OFFER_RE = re.compile(r"^\s*(\d+)\s*\+\s*(\d+)\s*$")

RETURN_MARKERS = ("مرد", "مرتجع")

# فواتير من نوع "م. مبيع" (تصحيحات/سحوبات مبيعات) مستبعدة كلياً من الحساب.
# تحقّق رقمي مباشر (2026-08-31): كل سطر بفاتورة تبدأ بـ"م. مبيع" غائب
# دائماً عن المرجع، وغالباً يترافق مع سطر بيع آخر (بنفس الكمية والهدايا
# ضمن نفس المادة وعرض المفرق) يُلغى معه. لا يشمل هذا بادئة "مسحوب" —
# محتسبة بالكامل دائماً — ولا بادئة "ح ه" (لا دليل عليها فتُركت كما هي).
EXCLUDED_INVOICE_PREFIXES = ("م. مبيع",)


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
        return Decimal(str(v))
    except InvalidOperation:
        return Decimal("0")


def parse_offer(raw) -> Optional[tuple]:
    """يرجع (صغير, كبير) كأعداد Decimal، أو None إن كان العرض '-' أو فارغاً أو غير مفهوم."""
    text = str(_clean(raw))
    if text in ("", "-", "0", "None"):
        return None
    m = OFFER_RE.match(text)
    if not m:
        return None
    large, small = Decimal(m.group(1)), Decimal(m.group(2))
    if large == 0:
        return None
    return small, large


def _has_value(raw) -> bool:
    """هل هذا العمود يحمل قيمة فعلية (وليس فارغاً/'-'/'0')؟ تُستخدم لفلتر
    'العروض المميزة فقط' (الخطوة 2) — بلا اشتراط أن تكون بصيغة رقم+رقم
    قابلة للتحليل، فقط وجود قيمة يكفي لاعتبار السطر مؤهلاً لدخول الفلتر."""
    text = str(_clean(raw))
    return text not in ("", "-", "0", "None")


def _is_return_invoice(invoice_text: str) -> bool:
    return any(marker in str(invoice_text or "") for marker in RETURN_MARKERS)


def is_excluded_invoice(invoice_text: str) -> bool:
    """فاتورة "م. مبيع" (تصحيح/سحب مبيعات) — مستبعدة كلياً من الحساب. انظر
    شرح EXCLUDED_INVOICE_PREFIXES أعلاه."""
    text = str(invoice_text or "").strip()
    return any(text.startswith(p) for p in EXCLUDED_INVOICE_PREFIXES)


@dataclass
class MovementRow:
    invoice: str
    date: str
    customer: str
    item: str
    retail_offer: str
    special_offer1: str
    special_offer: str
    qty: Decimal
    gifts: Decimal
    is_return: bool = False
    is_excluded_type: bool = False  # فاتورة "م. مبيع" — مستبعدة دائماً
    note: str = ""


def has_special_offer(row: "MovementRow") -> bool:
    """شرط الخطوة 2: يملك عرضاً مميزاً فعلياً في أحد العمودين."""
    return _has_value(row.special_offer1) or _has_value(row.special_offer)


REQUIRED_CLAIMS_COLS = {"المادة", "المطالبة"}
REQUIRED_MOVEMENT_COLS = {"الفاتورة", "التاريخ", "اسم الزبون", "اسم المادة", "كمية", "الهدايا"}


def _find_header(all_rows, required_cols, max_scan=12):
    for idx in range(min(max_scan, len(all_rows))):
        row = all_rows[idx]
        if not row:
            continue
        cells = {str(_clean(c)) for c in row if c is not None}
        if required_cols.issubset(cells):
            return idx, {str(_clean(c)): i for i, c in enumerate(row) if c is not None}
    raise ValueError("تعذّر العثور على صف العناوين المطلوب في الملف.")


def parse_claims_table(file_obj) -> dict:
    """يقرأ شيت 'مطالبات' (المادة / المطالبة) كمرجع معلوماتي فقط — يُعرض
    بجانب النتيجة الجديدة في التصدير للمقارنة، بلا أي تأثير على الحساب."""
    import openpyxl

    wb = openpyxl.load_workbook(file_obj, data_only=True, read_only=True)
    sheet = None
    for name in wb.sheetnames:
        if "مطالب" in name:
            sheet = name
            break
    if sheet is None:
        return {}
    ws = wb[sheet]
    rows = list(ws.iter_rows(values_only=True))
    if not rows:
        return {}
    try:
        header_idx, cols = _find_header(rows, REQUIRED_CLAIMS_COLS)
    except ValueError:
        return {}
    item_col = cols["المادة"]
    claim_col = cols["المطالبة"]
    out = {}
    for row in rows[header_idx + 1:]:
        if not row or row[item_col] in (None, ""):
            continue
        item = str(_clean(row[item_col]))
        out[item] = _to_decimal(row[claim_col])
    return out


def parse_daily_movement(file_obj) -> list[MovementRow]:
    """يقرأ شيت 'الحركة اليومية' الخام، مع تنفيذ الخطوة 1 (تعبئة رقم
    الفاتورة الصفري/الفارغ من السطر السابق) وتعليم أسطر المرتجعات."""
    import openpyxl

    wb = openpyxl.load_workbook(file_obj, data_only=True, read_only=True)
    sheet = None
    for name in wb.sheetnames:
        if "الحركة اليومية" in name or "حركة يومية" in name:
            sheet = name
            break
    if sheet is None:
        raise ValueError("لم يتم العثور على شيت 'الحركة اليومية' في الملف.")
    ws = wb[sheet]
    rows = list(ws.iter_rows(values_only=True))
    header_idx, cols = _find_header(rows, REQUIRED_MOVEMENT_COLS)

    c_inv = cols["الفاتورة"]
    c_date = cols["التاريخ"]
    c_cust = cols["اسم الزبون"]
    c_item = cols["اسم المادة"]
    c_retail = cols.get("عرض المفرق")
    c_special1 = cols.get("عرض مميز1")
    c_special = cols.get("عرض مميز")
    c_qty = cols["كمية"]
    c_gifts = cols["الهدايا"]

    out: list[MovementRow] = []
    last_invoice = ""
    for row in rows[header_idx + 1:]:
        if not row or row[c_item] in (None, ""):
            continue
        raw_inv = _clean(row[c_inv])
        inv_text = str(raw_inv)
        if raw_inv in (None, "", 0, "0"):
            inv_text = last_invoice  # الخطوة 1: تعبئة تنازلية من السطر السابق
        else:
            last_invoice = inv_text

        qty = _to_decimal(row[c_qty])
        gifts = _to_decimal(row[c_gifts])
        retail_raw = str(_clean(row[c_retail])) if c_retail is not None else "-"
        special1_raw = str(_clean(row[c_special1])) if c_special1 is not None else "-"
        special_raw = str(_clean(row[c_special])) if c_special is not None else "-"

        out.append(MovementRow(
            invoice=inv_text,
            date=str(_clean(row[c_date])),
            customer=str(_clean(row[c_cust])),
            item=str(_clean(row[c_item])),
            retail_offer=retail_raw or "-",
            special_offer1=special1_raw or "-",
            special_offer=special_raw or "-",
            qty=qty,
            gifts=gifts,
            is_return=_is_return_invoice(inv_text),
            is_excluded_type=is_excluded_invoice(inv_text),
        ))
    return out


def _find_pool_match(target_qty: Decimal, target_gifts: Decimal, candidates: list["MovementRow"]):
    """**تعديل 2026-10-04 بطلب المستخدم الصريح** (حالة حقيقية: مادة
    "غلوبيفيت كبير شراب 200 مل"، فاتورة "م. مبيع ج: 27" لـ"مستودع بركات-
    دمشق" بكمية 100 وهدايا 80 — لا يوجد لها سطر بيع واحد بنفس الكمية
    والهدايا بالضبط). شرح المستخدم حرفياً: "الفاتورة مرتجع مبيع ضمن
    مستودع بركات هية طلعت 100+80 اضطرينا نجمع من فواتير المبيعات...
    لحتى يطلع معنا 100+80". أي: فريق المالية يطابق تصحيح/مرتجع كبير
    الحجم مع **تجميع عدة فواتير بيع أصغر** (لا فاتورة واحدة) يكون مجموع
    كمياتها ومجموع هداياها معاً يطابق تماماً كمية وهدايا سطر التصحيح/
    المرتجع، ثم يُلغي الكل معاً (التصحيح + كل الفواتير المطابقة) تماماً
    كما تُلغى الأزواج المباشرة أعلاه.

    يبحث هنا عن **مجموعة فرعية** من `candidates` (أسطر بيع حقيقية ضمن
    نفس الحزمة مادة×عرض مفرق) يكون مجموع كمياتها = target_qty **و**
    مجموع هداياها = target_gifts معاً (الشرطان بآن واحد، وليس الكمية
    فقط) — بحث DP/تراجعي مجمَّع حسب قيمة (كمية, هدية) المتكررة لتبسيط
    المساحة (الأسطر المتماثلة كثيرة عملياً: عشرات الفواتير بنفس الزوج
    "10+8" أو "20+16" مثلاً)، يُفضَّل أقل عدد أسطر ممكن (الأكبر قيمة
    أولاً) ليسهل عرضها وتفسيرها للمستخدم. يرجع قائمة الأسطر المطابقة،
    أو None إن تعذّر إيجاد مطابقة تامة (تبقى الحالة الاستثنائية حينها
    بلا تغيير — تصحيح/مرتجع مستبعد بمفرده كالسابق)."""
    if target_qty <= 0 and target_gifts <= 0:
        return None
    groups: dict[tuple, list["MovementRow"]] = {}
    for r in candidates:
        groups.setdefault((r.qty, r.gifts), []).append(r)
    # تستبعد المجموعات التي لن تفيد أبداً (كمية وهدية صفريان معاً)
    keys = [k for k in groups if not (k[0] == 0 and k[1] == 0)]
    keys.sort(key=lambda k: (-k[0], -k[1]))  # الأكبر أولاً: يقلّل عدد الأسطر بالمطابقة
    counts = [len(groups[k]) for k in keys]

    memo: dict[tuple, object] = {}

    def rec(i: int, remaining_qty: Decimal, remaining_gifts: Decimal):
        if remaining_qty == 0 and remaining_gifts == 0:
            return []
        if i >= len(keys) or remaining_qty < 0 or remaining_gifts < 0:
            return None
        key = (i, remaining_qty, remaining_gifts)
        if key in memo:
            return memo[key]
        qty_v, gifts_v = keys[i]
        result = None
        use = counts[i]
        while use >= 0:
            nq = remaining_qty - qty_v * use
            ng = remaining_gifts - gifts_v * use
            if nq >= 0 and ng >= 0:
                sub = rec(i + 1, nq, ng)
                if sub is not None:
                    result = [(keys[i], use)] + sub
                    break
            use -= 1
        memo[key] = result
        return result

    plan = rec(0, target_qty, target_gifts)
    if plan is None:
        return None
    matched_rows: list["MovementRow"] = []
    for key, use in plan:
        if use <= 0:
            continue
        matched_rows.extend(groups[key][:use])
    return matched_rows


def _cancel_pairs_by_qty_gifts(rows: list[MovementRow], is_target) -> tuple[list[MovementRow], int, list[MovementRow], list[dict]]:
    """آلية إلغاء أزواج عامة تعمل **ضمن حزمة (مادة × عرض مفرق) واحدة
    فقط** — بمطابقة الكمية والهدايا حصراً، بلا أي اشتراط على الزبون
    (تصحيح 2026-08-31: 'للدقة رح نهمل الفلترة على اسم الصيدلية').
    `is_target(row)` يحدد أي الأسطر من النوع المطلوب إلغاؤه (مثل "م.
    مبيع" أو المرتجعات).

    **تعديل 2026-10-04:** إن لم يوجد سطر بيع واحد يطابق السطر المستهدف
    تماماً، يُحاوَل الآن (قبل اعتباره "بلا مطابقة") إيجاد **تجميع عدة
    فواتير بيع** (انظر `_find_pool_match` أعلاه) يطابق كميته وهداياه
    معاً بالضبط؛ إن وُجد يُحذف الكل معاً (كحالة الزوج المباشر)، ويُسجَّل
    بقائمة `pool_matches` منفصلة للتدقيق والعرض بشيت مخصص بالتصدير —
    بطلب المستخدم الصريح بعد شرح حالة فاتورة "م. مبيع ج: 27" الحقيقية.

    يرجع (الأسطر الباقية، عدد الأزواج المباشرة الملغاة معاً، الأسطر
    المستهدفة التي بقيت بلا أي مطابقة (مباشرة أو تجميع)، قائمة مطابقات
    التجميع [{'target': السطر المستهدف, 'matched': [أسطر البيع المطابقة]}])."""
    remaining = list(rows)
    cancelled_pairs = 0
    standalone: list[MovementRow] = []
    pool_matches: list[dict] = []
    targets = [r for r in remaining if is_target(r)]

    for t in targets:
        if t not in remaining:
            continue
        match = None
        for cand in remaining:
            if cand is t or is_target(cand):
                continue
            if cand.qty == t.qty and cand.gifts == t.gifts:
                match = cand
                break
        if match is not None:
            remaining.remove(t)
            remaining.remove(match)
            cancelled_pairs += 1
            continue

        pool_candidates = [r for r in remaining if r is not t and not is_target(r)]
        pool = _find_pool_match(t.qty, t.gifts, pool_candidates)
        if pool is not None and pool:
            remaining.remove(t)
            for r in pool:
                remaining.remove(r)
            pool_matches.append({"target": t, "matched": pool})
        else:
            remaining.remove(t)
            standalone.append(t)
    return remaining, cancelled_pairs, standalone, pool_matches


def cancel_mabee_pairs(rows: list[MovementRow]) -> tuple[list[MovementRow], int, list[MovementRow], list[dict]]:
    """يعالج فواتير "م. مبيع" ضمن حزمة (مادة × عرض مفرق) واحدة — مستبعدة
    دائماً من الحساب (انظر EXCLUDED_INVOICE_PREFIXES)، سواء وُجد سطر بيع
    مطابق واحد (بنفس الكمية والهدايا، بلا اشتراط الزبون)، أو تجميع عدة
    فواتير بيع يطابقها معاً (تعديل 2026-10-04 — انظر `_find_pool_match`)،
    أم لا يوجد أي مطابقة (تبقى مستبعدة بمفردها كالسابق)."""
    remaining, cancelled, standalone, pool_matches = _cancel_pairs_by_qty_gifts(rows, lambda r: r.is_excluded_type)
    for r in standalone:
        r.note = "فاتورة 'م. مبيع' (تصحيح/سحب مبيعات) — مستبعدة دائماً من الحساب، بلا سطر بيع مطابق (مفرد أو تجميع)"
    for pm in pool_matches:
        t = pm["target"]
        n = len(pm["matched"])
        t.note = (f"فاتورة 'م. مبيع' (تصحيح/سحب مبيعات) بكمية {t.qty} وهدايا {t.gifts} — "
                  f"أُلغيت بتجميع {n} فاتورة بيع (مجموع كمياتها وهداياها يطابقها تماماً)")
        for r in pm["matched"]:
            r.note = f"أُلغيت ضمن تجميع مقابل فاتورة 'م. مبيع' {t.invoice} (تصحيح/سحب مبيعات كبير الحجم)"
    return remaining, cancelled, standalone, pool_matches


def cancel_return_pairs(rows: list[MovementRow]) -> tuple[list[MovementRow], int, list[dict]]:
    """يلغي سطر المرتجع مع سطر البيع الذي يملك نفس الكمية والهدايا (بلا
    اشتراط الزبون، تصحيح 2026-08-31)، أو مع تجميع عدة فواتير بيع يطابقها
    معاً (تعديل 2026-10-04 — نفس آلية "م. مبيع" أعلاه)، ضمن حزمة (مادة ×
    عرض مفرق) واحدة. مرتجع بلا أي مطابقة (مفردة أو تجميع) يبقى ضمن
    البيانات ويُعلَّم للمراجعة، لا يُستبعد."""
    remaining, cancelled, standalone, pool_matches = _cancel_pairs_by_qty_gifts(rows, lambda r: r.is_return and not r.is_excluded_type)
    for r in standalone:
        # أُعيد سطر المرتجع بلا مطابقة إلى remaining (لا يُستبعد بمفرده)
        r.note = "مرتجع بدون سطر بيع مطابق (مفرد أو تجميع عدة فواتير) — بقي ضمن الحساب ليُراجع يدوياً"
        remaining.append(r)
    for pm in pool_matches:
        t = pm["target"]
        n = len(pm["matched"])
        t.note = f"مرتجع بكمية {t.qty} وهدايا {t.gifts} — أُلغي بتجميع {n} فاتورة بيع (مجموع كمياتها وهداياها يطابقه تماماً)"
        for r in pm["matched"]:
            r.note = f"أُلغيت ضمن تجميع مقابل المرتجع {t.invoice}"
    return remaining, cancelled, pool_matches


def merge_zero_qty_rows(rows: list[MovementRow]) -> tuple[list[MovementRow], int, list[MovementRow]]:
    """تعديل 2026-08-31 (ثالث): ضمن حزمة (مادة × عرض مفرق) واحدة، كل سطر
    كميته = صفر (لكن هداياه فعلية غالباً) يُدمَج مع سطر آخر **لنفس
    الزبون** (كمية غير صفرية إن أمكن) بإضافة هداياه إلى هدايا ذاك السطر،
    ثم يُحذف سطر الكمية=صفر بالكامل — بدل معالجته كسطر مستقل (كان
    سيُعطى بالنسخة السابقة ناتج معادلة = صفر وصافياً = هداياه كاملة، أي
    "ربح مجاني" غير صحيح). تحقّق رقمي مباشر (2026-08-31) بمثال حقيقي:
    فاتورة 'ع B: 32838' (كمية=0، هدايا=5، عرض 10+5) لصيدلية 'الزعيم -
    ساحة شمدين' دُمجت مع فاتورة 'ع B: 32677' لنفس الصيدلية (كمية=10،
    هدايا=6) لتصبح كمية=10، هدايا=11 (6+5) — مطابق تماماً لمثال زوّدنا
    به المستخدم بالصور.
    إن لم يوجد سطر آخر لنفس الزبون ضمن نفس الحزمة، يبقى سطر الكمية=صفر
    ظاهراً بمفرده (مُعلَّماً للمراجعة اليدوية) بدل حذفه بصمت.
    يرجع (الأسطر الباقية بعد الدمج والحذف، عدد الأسطر المدموجة والمحذوفة،
    قائمة أسطر الكمية=صفر التي بقيت بلا زبون آخر لدمجها معه)."""
    remaining = list(rows)
    zero_rows = [r for r in remaining if r.qty == 0]
    merged_count = 0
    unmerged: list[MovementRow] = []

    for zr in zero_rows:
        if zr not in remaining:
            continue
        sibling = None
        for cand in remaining:
            if cand is zr or cand.qty == 0:
                continue
            if cand.customer == zr.customer:
                sibling = cand
                break
        if sibling is not None:
            sibling.gifts += zr.gifts
            remaining.remove(zr)
            merged_count += 1
        else:
            zr.note = "سطر كمية = صفر بلا سطر آخر لنفس الزبون لدمج هداياه معه — بقي ظاهراً وحده للمراجعة"
            unmerged.append(zr)
    return remaining, merged_count, unmerged


@dataclass
class RowCalc:
    """نتيجة حساب سطر واحد بمفرده (الخطوات 6-7) — تُستخدم للتفصيل الكامل
    داخل شيت كل مادة (تدقيق سطراً بسطر يطابق شكل ملف المستخدم المرجعي:
    عمودا 'الإفرادي' و'السعر الإجمالي')."""
    row: MovementRow
    formula_result: Decimal    # "الإفرادي" — ناتج المعادلة لهذا السطر وحده
    net: Decimal               # "السعر الإجمالي" — هدايا السطر − ناتج معادلته
    included: bool             # صافي > 0 فقط يُحتسَب بالمجموع النهائي


@dataclass
class ClaimGroup:
    """مجموعة (مادة × عرض مفرق) — مستوى التجميع والنتيجة النهائي الجديد
    (بلا زبون، تصحيح 2026-08-31)."""
    item: str
    retail_offer: str
    qty: Decimal = Decimal("0")            # مجموع كمية الأسطر المُدرَجة فقط (صافيها > 0)
    gifts: Decimal = Decimal("0")          # مجموع هدايا الأسطر المُدرَجة فقط
    formula_result: Optional[Decimal] = None   # مجموع ناتج معادلة الأسطر المُدرَجة فقط
    claim_value: Optional[Decimal] = None      # = مجموع الهدايا − مجموع ناتج المعادلة (للأسطر المُدرَجة)
    row_calcs: list = field(default_factory=list)  # RowCalc لكل الأسطر (مُدرَجة ومستبعدة) — للتدقيق الكامل
    cancelled_mabee_pairs: int = 0
    excluded_mabee_rows: list = field(default_factory=list)
    pool_matched_mabee: list = field(default_factory=list)   # تعديل 2026-10-04 — [{'target','matched'}]
    cancelled_return_pairs: int = 0
    pool_matched_returns: list = field(default_factory=list)  # تعديل 2026-10-04 — [{'target','matched'}]
    merged_zero_qty_rows: int = 0
    unmerged_zero_qty_rows: list = field(default_factory=list)
    eligible: bool = True
    note: str = ""


def compute_bucket(item: str, retail_offer: str, rows: list[MovementRow]) -> ClaimGroup:
    """الخطوات 5-8 لحزمة (مادة × عرض مفرق) واحدة."""
    g = ClaimGroup(item=item, retail_offer=retail_offer)

    # الخطوة 5: إلغاء أزواج "م. مبيع" ثم أزواج المرتجع/المبيع — ضمن هذه
    # الحزمة فقط، بمطابقة الكمية والهدايا بلا اشتراط الزبون.
    remaining, g.cancelled_mabee_pairs, g.excluded_mabee_rows, g.pool_matched_mabee = cancel_mabee_pairs(rows)
    remaining, g.cancelled_return_pairs, g.pool_matched_returns = cancel_return_pairs(remaining)

    # تعديل 2026-08-31 (ثالث): دمج أسطر الكمية=صفر مع سطر آخر لنفس الزبون
    # (إضافة هداياها إليه) ثم حذفها بالكامل — قبل تطبيق المعادلة.
    remaining, g.merged_zero_qty_rows, g.unmerged_zero_qty_rows = merge_zero_qty_rows(remaining)

    retail = parse_offer(retail_offer)
    if retail is None:
        # تعديل 2026-09-26 بطلب المستخدم الصريح: "هناك عروض مميزة لا يوجد
        # لها عرض مفرق، أحتاج منك أن بهذه الحالة أن تجمع كل الهدايا للمادة
        # في حال وجود عرض مميز لها" — أي أن حزمة (مادة × عرض مفرق) بلا
        # قيمة "عرض مفرق" صالحة (وهي مؤهلة أصلاً بعرض مميز فعلي، وإلا لم
        # تكن لتصل هنا — انظر فلتر has_special_offer في process()) لم تعد
        # تُترك بمطالبة فارغة بانتظار مراجعة يدوية؛ بل تُحتسَب مطالبتها
        # مباشرة = مجموع كل هدايا أسطر الحزمة الباقية (بعد إلغاء أزواج "م.
        # مبيع"/المرتجعات ودمج أسطر الكمية=صفر أعلاه)، بلا أي طرح لناتج
        # معادلة — لأن المعادلة أصلاً تحتاج نسبة عرض مفرق غير متوفرة هنا.
        # يبقى العلم eligible=False (بمعنى: لم تُطبَّق معادلة عرض المفرق
        # على هذه الحزمة) للتمييز في شيت المراجعة المخصص، لكن قيمة
        # المطالبة لم تعد فارغة، وكل الأسطر تُعتبر "مُدرَجة" (لا يوجد هنا
        # مفهوم صافي سالب/موجب أصلاً بلا معادلة).
        g.eligible = False
        g.note = ("لا توجد قيمة 'عرض مفرق' صالحة لهذه الحزمة — تعذّر تطبيق المعادلة، "
                  "فاحتُسبت المطالبة كمجموع كل هدايا أسطر الحزمة مباشرة (بطلب المستخدم "
                  "الصريح 2026-09-26) بدل تركها فارغة للمراجعة اليدوية")
        g.qty = sum((r.qty for r in remaining), Decimal("0"))
        g.gifts = sum((r.gifts for r in remaining), Decimal("0"))
        g.formula_result = Decimal("0")
        g.claim_value = g.gifts
        g.row_calcs = [RowCalc(row=r, formula_result=Decimal("0"), net=r.gifts, included=True) for r in remaining]
        return g

    small, large = retail
    qty_sum = Decimal("0")
    gifts_sum = Decimal("0")
    formula_sum = Decimal("0")
    row_calcs = []
    for r in remaining:
        formula_result = (r.qty * small / large).quantize(Decimal("0.01"))
        net = r.gifts - formula_result
        included = net > 0
        row_calcs.append(RowCalc(row=r, formula_result=formula_result, net=net, included=included))
        if included:
            qty_sum += r.qty
            gifts_sum += r.gifts
            formula_sum += formula_result

    g.qty = qty_sum
    g.gifts = gifts_sum
    g.formula_result = formula_sum
    g.claim_value = gifts_sum - formula_sum
    g.row_calcs = row_calcs
    g.eligible = True
    return g


def compute_claim_groups(rows: list[MovementRow]) -> list[ClaimGroup]:
    """يبني حزم (مادة × عرض مفرق) من الأسطر بعد فلتر العروض المميزة، ثم
    يطبّق compute_bucket على كل حزمة على حدة — الخطوات 3-9 الجديدة."""
    buckets: dict[tuple, list[MovementRow]] = {}
    for r in rows:
        key = (r.item, r.retail_offer)
        buckets.setdefault(key, []).append(r)
    return [compute_bucket(item, retail_offer, bucket_rows)
            for (item, retail_offer), bucket_rows in buckets.items()]


def process(file_obj) -> dict:
    raw_rows = parse_daily_movement(file_obj)

    # الخطوة 2: فلترة "العروض المميزة فقط" — تُسقط تلقائياً كل مادة بلا أي
    # عرض مميز في كل الملف (بلا حاجة لفحص منفصل على مستوى المادة).
    offer_rows = [r for r in raw_rows if has_special_offer(r)]
    all_items = {r.item for r in raw_rows}
    offer_items = {r.item for r in offer_rows}
    ignored_items = sorted(all_items - offer_items)

    # الخطوات 3-9: تجميع (مادة × عرض مفرق) بلا زبون، إلغاء الأزواج ضمن كل
    # حزمة، معادلة لكل سطر بمفرده، حذف الأسطر ذات الصافي السالب/الصفري،
    # ثم جمع الأسطر الباقية فقط.
    claim_groups = compute_claim_groups(offer_rows)

    excluded_mabee_rows: list[MovementRow] = []
    cancelled_mabee_pairs = 0
    cancelled_return_pairs = 0
    unmatched_returns: list[MovementRow] = []
    excluded_nonpositive_rows: list = []  # عناصر RowCalc غير المُدرَجة (صافٍ ≤ صفر)
    merged_zero_qty_rows = 0
    unmerged_zero_qty_rows: list[MovementRow] = []
    pool_matches: list[dict] = []  # تعديل 2026-10-04 — كل مطابقات التجميع (م. مبيع + مرتجعات)، لكل الحزم

    for g in claim_groups:
        excluded_mabee_rows.extend(g.excluded_mabee_rows)
        cancelled_mabee_pairs += g.cancelled_mabee_pairs
        cancelled_return_pairs += g.cancelled_return_pairs
        merged_zero_qty_rows += g.merged_zero_qty_rows
        unmerged_zero_qty_rows.extend(g.unmerged_zero_qty_rows)
        for pm in (g.pool_matched_mabee + g.pool_matched_returns):
            pool_matches.append({"item": g.item, "retail_offer": g.retail_offer, **pm})
        for rc in g.row_calcs:
            if rc.row.is_return and "بدون سطر بيع مطابق" in (rc.row.note or ""):
                unmatched_returns.append(rc.row)
            if g.eligible and not rc.included:
                excluded_nonpositive_rows.append(rc)

    per_item: dict[str, list[ClaimGroup]] = {}
    for g in claim_groups:
        per_item.setdefault(g.item, []).append(g)

    eligible_groups = [g for g in claim_groups if g.eligible]
    ineligible_groups = [g for g in claim_groups if not g.eligible]

    total_qty = sum((g.qty for g in claim_groups), Decimal("0"))
    total_gifts = sum((g.gifts for g in claim_groups), Decimal("0"))
    total_formula_result = sum((g.formula_result or Decimal("0")) for g in claim_groups)
    total_claim_value = sum((g.claim_value or Decimal("0")) for g in claim_groups)

    return {
        "raw_row_count": len(raw_rows),
        "offer_row_count": len(offer_rows),
        "ignored_items": ignored_items,
        "ignored_items_count": len(ignored_items),
        "cancelled_mabee_pairs": cancelled_mabee_pairs,
        "excluded_mabee_rows": excluded_mabee_rows,
        "excluded_mabee_rows_count": len(excluded_mabee_rows),
        "cancelled_pairs": cancelled_return_pairs,
        "unmatched_returns": unmatched_returns,
        "unmatched_returns_count": len(unmatched_returns),
        "excluded_nonpositive_rows": excluded_nonpositive_rows,
        "excluded_nonpositive_rows_count": len(excluded_nonpositive_rows),
        "merged_zero_qty_rows": merged_zero_qty_rows,
        "unmerged_zero_qty_rows": unmerged_zero_qty_rows,
        "unmerged_zero_qty_rows_count": len(unmerged_zero_qty_rows),
        "claim_groups": claim_groups,
        "eligible_groups": eligible_groups,
        "ineligible_groups": ineligible_groups,
        "per_item": per_item,
        "items_count": len(per_item),
        "groups_count": len(claim_groups),
        "total_qty": total_qty,
        "total_gifts": total_gifts,
        "total_formula_result": total_formula_result,
        "total_claim_value": total_claim_value,
        "pool_matches": pool_matches,
        "pool_matches_count": len(pool_matches),
        "pool_matched_rows_count": sum(len(pm["matched"]) for pm in pool_matches),
    }
