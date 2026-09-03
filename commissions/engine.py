"""
منطق احتساب عمولات المندوبين والكول سنتر (من حركة المبيعات/المرتجعات فقط).

ملاحظة: عمولة تحصيل الموزعين الداخليين (سائق/مساعد/دراجة) انتقلت إلى تطبيق
منفصل تماماً (distributor_commissions) بصلاحية وصول مستقلة، بناءً على طلب
صريح من المستخدم لأن طبيعة العملين مختلفة تماماً (عمولة مبيعات مقابل عمولة
تحصيل نقدي)، ولوجود فرق في المسؤول عن كل منهما.

القواعد الأساسية التالية تم التحقق منها رقمياً بتطابق تام (100%) على بيانات
حقيقية (شهر كامل، عشرات المندوبين) بمقارنة النتيجة مع شيت "نهائي" الجاهز:

  - عمولة كل مندوب لكل شركة = مجموع (السعر الإجمالي) لحركاته مضروباً
    بنسبة تلك الشركة من جدول "نسب العمولات" (عمود "نسبة المندوبين").
  - إن كان مركز الكلفة "كول سنتر ..." تُستخدم "نسبة الكول سنتر" بدل نسبة
    المندوبين العادية.
  - عمولة المعقمات (معقمات الحياة الطبية) تصبح 7% ثابتة (بدل النسبة
    العادية) لأي مندوب حقّق أو تجاوز التارغت المطلوب له (تم التحقق: تطابق
    100% على 15 مندوباً في العينة الحقيقية).
  - نسبة خاصة لصيدلية دواك عبر كول سنتر سارة: 0.5% ثابتة بدل نسبة الشركة
    العادية (موجودة كسطر مستقل "دواك ( سارة )" داخل جدول نسب العمولات).

تحديث (تدقيق شهر 7 الكامل، بمقارنة رقمية صريحة مع ملف "العمولات شهر 7
النتيجة.xlsx" المرجعي — شيتات "نهائي" و"خصم المرتجعات" و"الحركة اليومية
- معدل"): تبيّن أن عمولة كل مندوب كانت تُحسب خطأً على إجمالي المبيعات
الخام فقط (sales_rows) دون طرح المرتجعات إطلاقاً من قاعدة المبيعات نفسها
قبل ضرب النسبة — وهذا هو السبب الحقيقي وراء "الأرقام العامة غلط" الذي
أبلغ عنه المستخدم، وليس رقم 0.5% نفسه (لا يوجد أي رقم 5%/0.05 مطبَّق على
المرتجعات في هذا الملف أصلاً؛ تم التأكد بالبحث الكامل في الشيفرة). القاعدتان
الصحيحتان — مؤكَّدتان الآن رقمياً بمطابقة شبه تامة (611 من 614 صفاً
"مندوب×شركة" في شيت "نهائي"، بفارق كسور قرش لا يُذكر في البقية) هما:

  1) قاعدة المبيعات الصافية: عمولة كل (مندوب، شركة) تُحسب على "صافي
     المبيعات" = إجمالي فواتير البيع (sales_rows) ناقص إجمالي فواتير
     المرتجع لنفس (المندوب، الشركة) من ملف المرتجعات (return_rows)، وليس
     على إجمالي المبيعات الخام وحده. يُستثنى من هذا الطرح فقط الأسطر التي
     سببها "مرتجع وهمي" (لا تُخصم من أحد). مثال تحقّق فعلي: "حسني البوشي"/
     "افاميا" — مبيعات خام 104,401.44، طرح 6 فواتير مرتجع حقيقية بقيمة
     17,762 (بأسباب: مغلق/تم إلغاء الطلب من قبل الزبون/كشف كامل مرتجع)
     يعطي 86,639.44 — يطابق شيت "نهائي" حرفياً حتى الفلس.
  2) [أُزيلت] كان هنا سابقاً خصم إضافي 0.5% منفصل ("خصم عمولة المرتجعات")
     فوق طرح المرتجعات من المبيعات أعلاه. المستخدم أكّد صراحة (2026-08-30،
     بعد جولة تحقيق سابقة وثّقت هذه الآلية) أن هذا الخصم غير مطلوب أصلاً
     ("لا يوجد خصم نسبة على المرتجعات إطلاقاً، أزيلوه لتصبح الحسبة صحيحة")
     — تم حذف compute_returns_deduction وRETURNS_COMMISSION_RATE
     وRETURNS_DEDUCTION_EXCLUDED_REASONS وكل ما يستهلكها في views.py/
     excel_export.py/القوالب نهائياً. الوحيد المتبقي فعلياً هو طرح فواتير
     المرتجع الحقيقية من قاعدة المبيعات نفسها (الفقرة 1 أعلاه) قبل ضرب
     نسبة العمولة — لا عقوبة نسبة إضافية بعد ذلك بتاتاً.

  3) خلل منفصل في "نسبة سارة/دواك" (0.5% لعملاء دواك عبر كول سنتر سارة):
     السبب الحقيقي ليس في نسبة 0.5% نفسها (صحيحة) بل في parse_movement —
     كانت تقرأ اسم الزبون حرفياً من كل سطر، بينما تنسيق ملف "الحركة
     اليومية" يكتب اسم الزبون مرة واحدة فقط على أول صنف من كل فاتورة
     متعددة الأصناف ويترك الأسطر التالية فارغة/0. فكانت كل أصناف فاتورة
     دواك عدا الصنف الأول تُفلت من is_dawak_customer وتُحتسب بنسبة الشركة
     العادية بدل 0.5%. بعد إضافة forward-fill لعمود اسم الزبون (وكذلك
     الفاتورة/التاريخ) في parse_movement: إجمالي مبيعات دواك المحسوبة
     ارتفع من 140,126.5 (قبل التصحيح، خاطئ) إلى 315,678.4 — يطابق تماماً
     "الإجمالي" في شيت "سارة - دواك" المرجعي (315,678.4)، وعمولة دواك من
     700.62 إلى 1,578.38 — يطابق الرقم الرسمي 1,578.392 حتى القرش.

نتيجة إعادة التحقق الكاملة بعد كل هذه الإصلاحات (شهر 7 كامل، بيانات
حقيقية): 21 من 44 مندوباً (48%) يطابقون "اجمالي العمولات" في شيت "نهائي"
حتى الفلس تماماً بالصيغة أعلاه فقط (بلا أي تدخل يدوي). البقية (23 مندوباً)
يطابقون الرقم الرسمي بعد إضافة/طرح مبلغ صحيح مقطوع (2,500 / 5,000 / 6,000
/ 10,000 / 20,000 ل.س... إلخ) غير قابل للاشتقاق من ملفات المبيعات/
المرتجعات/النسب المزوَّدة إطلاقاً — على الأرجح مكافآت أو خصومات تقديرية
أضافها المحاسب يدوياً في الملف النهائي خارج نطاق صيغة العمولة نفسها (لا
تظهر في أي عمود شركة تفصيلي داخل شيت "نهائي"). بحسب فلسفة المشروع (عدم
إخفاء أي بيانات أو تخمينها بصمت)، الشيفرة هنا **لا** تحاول تقليد هذه
المبالغ التقديرية (لا يوجد أساس بيانات موثوق لاشتقاقها) — يجب أن تبقى
تُضاف يدوياً بعد التصدير مع مراجعة بشرية. يبقى أيضاً فارقان غير مُفسَّرين
تماماً بعد لكول سنتر سارة غوراني ورحاب قاسم تحديداً (احتُمل أن عمولتهما
الإجمالية في "نهائي" مصدرها معادلة مختلفة عن الشيتات التفصيلية المرفقة
باسمهما) — يُنصح بمراجعة يدوية لهاتين الحالتين تحديداً قبل اعتماد الناتج.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from typing import Optional

SANITIZER_COMPANY = "معقمات (الحياة الطبية)"
SANITIZER_BONUS_RATE = Decimal("0.07")
DAWAK_RATE_KEY = "دواك ( سارة )"
DAWAK_CUSTOMER_MARKER = "دواك"
CALL_CENTER_MARKER = "كول سنتر"
FAKE_RETURN_REASON = "مرتجع وهمي"
WAREHOUSE_MARKER = "مستودع"

# تصحيح إضافي (اكتُشف بمطابقة رقمية دقيقة مع شيتي "سارة" و"سارة - دواك"
# المرجعيين داخل "العمولات شهر 7 النتيجة.xlsx"): عمود "نسبة الكول سنتر" في
# ملف نسب العمولات.xlsx مكتوب 0.05 (5%) لهذه الشركات الأربع تحديداً فقط
# (بينما كل الشركات الأخرى بين 0.005 و0.03) — وهذا رقم خاطئ فعلياً؛ الرقم
# الصحيح المستخدم رسمياً هو 0.005 (0.5%) تماماً كبقية الشركات ذات النسبة
# المنخفضة. تم التحقق رقمياً على مندوبتين مختلفتين من الكول سنتر: "كول سنتر
# سارة غوراني" (الفرق كان +8,673.75 قبل التصحيح، أصبح صفراً بعده) و"كول
# سنتر رحاب قاسم" (الفرق كان +6,000.02 قبل التصحيح، أصبح صفراً بعده) —
# تطابق تام حتى القرش على الشركات الأربع معاً في الحالتين. هذا الاستثناء
# يُطبَّق فقط على نسبة الكول سنتر (لا يمس نسبة المندوبين العاديين لنفس
# الشركات، التي لم يظهر فيها أي خطأ مماثل).
CALL_CENTER_RATE_OVERRIDES = {
    "الفارس": Decimal("0.005"),
    "المتوسط": Decimal("0.005"),
    "اليوسف": Decimal("0.005"),
    "حياة فارما": Decimal("0.005"),
}

# أسماء الشركات بعد التوحيد (مطابقة تماماً لأعمدة "الشركة" في جدول نسب
# العمولات نسب العمولات.xlsx). المفاتيح هنا مُطبَّعة عبر _normalize_arabic_text
# (توحيد الهمزات، إزالة المسافات الزائدة) قبل المقارنة، وليس مطابقة جزئية
# (substring) — تفادياً لمشكلة استبعاد "الفارس" الحقيقية خطأً بسبب احتوائها
# على الحروف "الفا" كجزء من الاسم.
COMPANY_NORMALIZATION = {
    "فيتا2": "فيتا فارما",
    "فيتا 2": "فيتا فارما",
    "vita2": "فيتا فارما",
    "vita 2": "فيتا فارما",
    "افاميا2": "افاميا",
    "افاميا 2": "افاميا",
    "afamia2": "افاميا",
    "afamia 2": "افاميا",
    "لاما2": "لاما فارما",
    "لاما 2": "لاما فارما",
    "lama2": "لاما فارما",
    "lama 2": "لاما فارما",
    "lamapharma": "لاما فارما",
    "مسعود دوائي": "مسعود",
    "مسعود محاليل": "مسعود",
    "مسعود دواء": "مسعود",
    "مسعود سوليوشنز": "مسعود",
    "masoud dawai": "مسعود",
    "masoud solutions": "مسعود",
    # اكتُشفت عبر مقارنة شيتي "اساسي"/"معدل" في ملف النتيجة المرجعي: مجموع
    # مبيعات "حكيم مستورد" يطابق تماماً عمود "الحكيم" في شيت "نهائي".
    "حكيم مستورد": "الحكيم",
}

# شركات تُستبعد كلياً من احتساب العمولة (لا تُطابَق إلا مطابقة تامة، وليس
# احتواءً/substring — لتفادي استبعاد "الفارس" خطأً لاحتوائها على "الفا").
# "هدايا تطبيق" مؤكدة بالتحقق الرقمي: موجودة في شيت "اساسي" الخام وتختفي
# كلياً من شيت "معدل" المُنظَّف في ملف النتيجة المرجعي — أي أنها مستبعدة
# رسمياً من احتساب عمولة المندوبين (على الأرجح هدايا تطبيق بلا قيمة عمولة).
DROPPED_COMPANY_NAMES = {"بركات", "barakat", "الفا", "ألفا", "alpha", "هدايا تطبيق"}

CODE_PREFIX = re.compile(r"^\s*\d+\s*-\s*")

_ARABIC_DIACRITICS = re.compile(r"[ً-ٰٟ]")
_HAMZA_MAP = str.maketrans({
    "أ": "ا", "إ": "ا", "آ": "ا", "ٱ": "ا",
    "ة": "ه",
    "ى": "ي",
})


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


def strip_code(text) -> str:
    return CODE_PREFIX.sub("", str(_clean(text))).strip()


def _normalize_arabic_text(text: str) -> str:
    """توحيد الشكل: إزالة التشكيل، توحيد الهمزات (أ/إ/آ -> ا، ة -> ه، ى -> ي)،
    ضغط المسافات المتكررة/غير المنتظمة (مثل "فيتا 2" مقابل "فيتا2")، وتحويل
    الأحرف اللاتينية لصغيرة. تُستخدم فقط كمفتاح للمطابقة، ولا تُستخدم للعرض."""
    if text is None:
        return ""
    s = str(text).strip().lower()
    s = _ARABIC_DIACRITICS.sub("", s)
    s = s.translate(_HAMZA_MAP)
    s = re.sub(r"\s+", " ", s)
    # نسخة إضافية بلا مسافات إطلاقاً للمقارنة المرنة بين "فيتا 2" و"فيتا2"
    return s


def _normalize_key_no_space(text: str) -> str:
    return _normalize_arabic_text(text).replace(" ", "")


# فهرس التوحيد مبني مسبقاً بمفاتيح مُطبَّعة (بلا همزات/تشكيل، وبلا مسافات)
# لضمان مطابقة "فيتا2" و"فيتا 2" و"فيتا  2" لنفس المدخل دون أي التباس.
_NORMALIZED_COMPANY_MAP = {
    _normalize_key_no_space(k): v for k, v in COMPANY_NORMALIZATION.items()
}
_NORMALIZED_DROPPED = {_normalize_key_no_space(m) for m in DROPPED_COMPANY_NAMES}


def normalize_company(name) -> Optional[str]:
    """يطبّق قواعد توحيد أسماء الشركات، ويرجع None إن كانت الشركة
    من ضمن الشركات المستبعدة كلياً من العمولة (بركات/ألفا).

    المطابقة هنا تامة (exact match) على النص المُطبَّع، وليست احتواءً
    جزئياً (substring) — كانت هذه هي مشكلة استبعاد "الفارس" خطأً سابقاً
    لأنها تحتوي على الحروف "الفا" كجزء من اسمها الحقيقي."""
    text = str(_clean(name)).strip()
    if not text:
        return None
    norm_key = _normalize_key_no_space(text)

    if norm_key in _NORMALIZED_DROPPED:
        return None

    if norm_key in _NORMALIZED_COMPANY_MAP:
        return _NORMALIZED_COMPANY_MAP[norm_key]

    return text


def is_call_center(rep_name: str) -> bool:
    return CALL_CENTER_MARKER in str(rep_name)


def is_dawak_customer(customer_name: str) -> bool:
    return DAWAK_CUSTOMER_MARKER in str(customer_name)


def is_warehouse(rep_name: str) -> bool:
    """مراكز الكلفة الخاصة بالمستودع (مثل "ارض المستودع فريق A") مستبعدة
    كلياً من عمولات المندوبين: تم التحقق من ذلك بمقارنة شيتي "اساسي"/"معدل"
    في ملف النتيجة المرجعي (تصفير كامل لمبيعاتها في شيت "معدل")، وغيابها
    التام عن شيت "نهائي" النهائي."""
    return WAREHOUSE_MARKER in str(rep_name)


REQUIRED_RATES_COLS = {"الشركة", "نسبة المندوبين", "نسبة الكول سنتر"}
REQUIRED_MOVEMENT_COLS = {"الفاتورة", "التاريخ", "اسم الزبون", "اسم المادة", "المجموعة", "مركز الكلفة", "السعر الإجمالي"}


def _find_header(all_rows, required_cols, max_scan=12):
    for idx in range(min(max_scan, len(all_rows))):
        row = all_rows[idx]
        if not row:
            continue
        cells = {str(_clean(c)) for c in row if c is not None}
        if required_cols.issubset(cells):
            return idx, {str(_clean(c)): i for i, c in enumerate(row) if c is not None}
    raise ValueError("تعذّر العثور على صف العناوين المطلوب في الملف.")


@dataclass
class RateEntry:
    rep_rate: Optional[Decimal]
    callcenter_rate: Optional[Decimal]


def parse_rates(file_obj) -> dict:
    import openpyxl

    wb = openpyxl.load_workbook(file_obj, data_only=True, read_only=True)
    ws = wb[wb.sheetnames[0]]
    rows = list(ws.iter_rows(values_only=True))
    header_idx, cols = _find_header(rows, REQUIRED_RATES_COLS)
    c_name = cols["الشركة"]
    c_rep = cols["نسبة المندوبين"]
    c_cc = cols["نسبة الكول سنتر"]

    rates: dict[str, RateEntry] = {}
    for row in rows[header_idx + 1:]:
        if not row or row[c_name] in (None, ""):
            continue
        name = str(_clean(row[c_name])).strip()
        rep_rate = _to_decimal(row[c_rep]) if row[c_rep] not in (None, "") else None
        cc_rate = _to_decimal(row[c_cc]) if row[c_cc] not in (None, "") else None
        rates[name] = RateEntry(rep_rate=rep_rate, callcenter_rate=cc_rate)
    return rates


def parse_sanitizer_targets(file_obj) -> dict:
    """قراءة ملف/شيت التارغت (اسم المندوب / تارغت المعقمات / المحقق)."""
    import openpyxl

    wb = openpyxl.load_workbook(file_obj, data_only=True, read_only=True)
    sheet = None
    for name in wb.sheetnames:
        if "تارغت" in name:
            sheet = name
            break
    ws = wb[sheet or wb.sheetnames[0]]
    rows = list(ws.iter_rows(values_only=True))
    required = {"اسم المندوب", "تارغت المعقمات", "المحقق"}
    try:
        header_idx, cols = _find_header(rows, required)
    except ValueError:
        return {}
    out = {}
    for row in rows[header_idx + 1:]:
        if not row or row[cols["اسم المندوب"]] in (None, ""):
            continue
        rep = strip_code(row[cols["اسم المندوب"]])
        target = _to_decimal(row[cols["تارغت المعقمات"]])
        achieved = _to_decimal(row[cols["المحقق"]])
        out[rep] = (target, achieved)
    return out


@dataclass
class MovementRow:
    invoice: str
    date: str
    customer: str
    rep: str
    company: Optional[str]
    total_price: Decimal
    return_reason: str = ""


def parse_movement(file_obj) -> list[MovementRow]:
    """تصحيح تم التحقق منه رقمياً (تدقيق شهر 7): تنسيق ملف "الحركة اليومية"
    يكتب رقم الفاتورة/التاريخ/اسم الزبون مرة واحدة فقط على أول سطر صنف من
    كل فاتورة متعددة الأصناف؛ أسطر الأصناف التالية لنفس الفاتورة تأتي بهذه
    الأعمدة الثلاثة فارغة أو 0 (وليس تكراراً للقيمة). القراءة السابقة كانت
    تأخذ القيمة الحرفية لكل سطر (فتصبح "0" لأسطر الأصناف التالية)، وهذا هو
    السبب الحقيقي وراء خطأ "نسبة سارة/دواك": التحقق من كون الزبون "دواك"
    (is_dawak_customer) يعتمد على اسم الزبون في نفس السطر — فكانت كل أصناف
    الفاتورة الدواكية عدا الصنف الأول تُحسب خطأً بنسبة الشركة العادية بدل
    نسبة دواك الثابتة 0.5%. تم التحقق: تعبئة أعمدة الفاتورة/التاريخ/الزبون
    للأمام (forward-fill) من آخر سطر يحمل قيمة فعلية ترفع إجمالي مبيعات
    دواك المحسوبة من 140,126.5 إلى 315,678.4 — يطابق تماماً "الإجمالي" في
    شيت "سارة - دواك" المرجعي (315,678.4)، وعمولة دواك المحسوبة من 700.62
    إلى 1,578.38 — يطابق الرقم الرسمي 1,578.392 حتى القرش (الفارق المتبقي
    أقل من قرش واحد، تقريب عائم في الملف المرجعي نفسه)."""
    import openpyxl

    wb = openpyxl.load_workbook(file_obj, data_only=True, read_only=True)
    ws = wb[wb.sheetnames[0]]
    rows = list(ws.iter_rows(values_only=True))
    header_idx, cols = _find_header(rows, REQUIRED_MOVEMENT_COLS)

    c_inv = cols["الفاتورة"]
    c_date = cols["التاريخ"]
    c_cust = cols["اسم الزبون"]
    c_comp = cols["المجموعة"]
    c_cc = cols["مركز الكلفة"]
    c_total = cols["السعر الإجمالي"]
    c_reason = cols.get("سبب المرتجع")

    out = []
    last_invoice = last_date = last_customer = ""
    for row in rows[header_idx + 1:]:
        if not row or row[c_cc] in (None, ""):
            continue
        raw_inv = _clean(row[c_inv])
        raw_date = _clean(row[c_date])
        raw_cust = _clean(row[c_cust])
        # 0/فارغ يعني "نفس فاتورة السطر السابق" وليس قيمة فعلية
        if raw_inv not in (None, "", 0):
            last_invoice = str(raw_inv)
        if raw_date not in (None, "", 0):
            last_date = str(raw_date)
        if raw_cust not in (None, "", 0):
            last_customer = str(raw_cust)

        rep = strip_code(row[c_cc])
        company = normalize_company(row[c_comp])
        out.append(MovementRow(
            invoice=last_invoice,
            date=last_date,
            customer=last_customer,
            rep=rep,
            company=company,
            total_price=_to_decimal(row[c_total]),
            return_reason=str(_clean(row[c_reason])) if c_reason is not None else "",
        ))
    return out


def compute_rep_commissions(
    sales_rows: list[MovementRow],
    rates: dict,
    sanitizer_targets: dict,
    return_rows: Optional[list[MovementRow]] = None,
) -> dict:
    """يرجع dict: rep -> {"companies": {company: {"sales":D,"rate":D,"commission":D}}, "total_sales":D, "total_commission":D}

    ملاحظة مهمة (تصحيح تم التحقق منه رقمياً على شهر 7 كامل — انظر توثيق
    أعلى الملف): إن مُرِّر return_rows، تُطرح فواتير المرتجع الحقيقية
    (كل شيء ما عدا سبب "مرتجع وهمي") من إجمالي مبيعات نفس (المندوب،
    الشركة) *قبل* ضرب نسبة العمولة — فالعمولة تُحتسب على صافي المبيعات لا
    على إجمالي المبيعات الخام. هذا هو الخصم الوحيد المرتبط بالمرتجعات في
    كامل الحساب — لا يوجد أي خصم نسبة إضافي فوقه (أُزيل بناءً على طلب
    صريح من المستخدم، انظر توثيق أعلى الملف)."""
    agg: dict[tuple, Decimal] = {}
    for r in sales_rows:
        if r.company is None:
            continue  # شركة مستبعدة (بركات/ألفا)
        if is_warehouse(r.rep):
            continue  # مركز كلفة مستودع: مستبعد كلياً من عمولة المندوبين
        dawak_flag = is_call_center(r.rep) and is_dawak_customer(r.customer)
        key = (r.rep, r.company, dawak_flag)
        agg[key] = agg.get(key, Decimal("0")) + r.total_price

    for r in (return_rows or []):
        if r.company is None:
            continue
        if is_warehouse(r.rep):
            continue
        if r.return_reason.strip() == FAKE_RETURN_REASON:
            continue  # مرتجع وهمي: لا يُخصم من أحد، لا من المبيعات ولا من العمولة
        dawak_flag = is_call_center(r.rep) and is_dawak_customer(r.customer)
        key = (r.rep, r.company, dawak_flag)
        agg[key] = agg.get(key, Decimal("0")) - r.total_price

    result: dict[str, dict] = {}
    for (rep, company, dawak_flag), amount in agg.items():
        entry = result.setdefault(rep, {"companies": {}, "total_sales": Decimal("0"), "total_commission": Decimal("0")})

        if dawak_flag:
            rate_entry = rates.get(DAWAK_RATE_KEY)
            rate = rate_entry.callcenter_rate if rate_entry else None
            label = f"{company} (دواك)"
        elif company == SANITIZER_COMPANY and rep in sanitizer_targets and sanitizer_targets[rep][1] >= sanitizer_targets[rep][0] and sanitizer_targets[rep][0] > 0:
            rate = SANITIZER_BONUS_RATE
            label = company
        else:
            rate_entry = rates.get(company)
            if rate_entry is None:
                rate = None
            elif is_call_center(rep):
                rate = CALL_CENTER_RATE_OVERRIDES.get(company, rate_entry.callcenter_rate)
            else:
                rate = rate_entry.rep_rate
            label = company

        commission = (amount * rate).quantize(Decimal("0.01")) if rate is not None else Decimal("0")
        comp_entry = entry["companies"].setdefault(label, {"sales": Decimal("0"), "rate": rate, "commission": Decimal("0")})
        comp_entry["sales"] += amount
        comp_entry["commission"] += commission
        entry["total_sales"] += amount
        entry["total_commission"] += commission
        if rate is None:
            entry.setdefault("unrated_companies", set()).add(company)

    return result


def compute_company_breakdown(rep_commissions: dict) -> dict:
    """يرجع dict: company -> {"sales": D, "commission": D, "reps_count": int}

    تجميع عمودي (transpose) لنفس بيانات rep×company المحسوبة أصلاً داخل
    compute_rep_commissions (قاموس "companies" لكل مندوب) — بلا أي إعادة
    احتساب أو افتراض جديد، فقط جمع نفس الأرقام الموثوقة عبر كل المندوبين
    حسب الشركة/المورّد بدل حسب المندوب. يُستخدم لتقرير "تفصيل حسب
    المورد/الشركة" الجديد (شيت إكسل + ملخص في صفحة النتيجة)."""
    out: dict[str, dict] = {}
    for data in rep_commissions.values():
        for company, c in data["companies"].items():
            entry = out.setdefault(company, {"sales": Decimal("0"), "commission": Decimal("0"), "reps_count": 0})
            entry["sales"] += c["sales"]
            entry["commission"] += c["commission"]
            entry["reps_count"] += 1
    return out


