"""
منطق احتساب عمولة تحصيل الموزعين الداخليين (سائق/مساعد/دراجة) ومرتجعاتهم.

هذه الوحدة منفصلة تماماً عن وحدة "عمولات المندوبين" — تعتمد على دفتر أستاذ
ذمم قسم التوزيع ("دفتر الأستاذ") وشيت المرتجعات ("مرتجعات") فقط، وتحتسب
عمولة تحصيل الدفعات النقدية من الصيدليات (وليس عمولة مبيعات).

تم اشتقاق قواعد الاحتساب أدناه بالتحقق الشامل (مطابقة كل سيناريو ممكن دون
استثناء) على شهر مرجعي كامل زوّدنا به المستخدم (يتضمن شيت "تقرير نتيجة "
كمرجع صحيح)، وليس فقط من الوصف الشفهي الأصلي. أهم فروقات النتيجة عن الوصف
الحرفي موثّقة في التعليقات أدناه لكل حالة.

جدول النسب المتحقق منه (تحصيل نقدي):
  - شخص واحد فقط (منفرد):
      * سائق سيارة / مساعد سائق  -> 0.4%
      * سائق دراجة (أي عمود من عمودي الدراجة) -> 0.25%
      * استثناء بدون حالة "منفرد" موثّقة هذا الشهر؛ نفترض 0.4% (فئة سيارة) قياساً.
  - شخصان:
      * سيارة+سيارة، أو سيارة+دراجة (مختلط): 0.25% لكل منهما، بلا استثناء.
      * دراجة+دراجة (كلاهما فئة دراجة): 0.125% لكل منهما (نصف النسبة أعلاه) —
        تصحيح 2026-09-28 (بلاغ مستخدم صريح + تحقّق رقمي كامل مقابل ملف "نقدية
        الموزعين شهر 8" المرجعي: 4345 حركة سيارة+سيارة و531 حركة مختلطة كلها
        0.25%/كل مشارك بلا استثناء، مقابل 119 حركة دراجة+دراجة كلها 0.125%
        بالضبط بلا استثناء — راجع _pair_rate في قسم الاحتساب أدناه). قبل هذا
        التصحيح كانت كل حالات "شخصان" تُعامَل بنسبة واحدة موحّدة 0.25% بصرف
        النظر عن الفئة؛ هذا كان خطأً لحالة دراجة+دراجة تحديداً فقط.
  - ثلاثة أشخاص: كل شخص حسب فئته الخاصة (وليس علماً واحداً على مستوى الحركة كلها):
      * فئة سيارة (سائق/مساعد/استثناء): 0.5%/3 لكل منهم
      * فئة دراجة (دراجة/دراجة 2): 0.25%/3 لكل منهم
  - أربعة فأكثر: لم يظهر أي مثال هذا الشهر. نطبّق نفس منطق فئة الثلاثة
    (قسمة ثابتة على 3 كما ورد حرفياً من المستخدم)، وتُعلَّم هذه الحركات
    للمراجعة اليدوية لعدم وجود بيانات مرجعية تؤكدها.

استثناء أسماء (سائقو دراجات مسجّلون أحياناً بعمود "موزع السائق" سهواً):
  كريم هاشم، مراد علوش -> يُعامَلان دائماً كفئة دراجة (0.25% لحالة "منفرد"،
  والتقسيم الخاص بفئة الدراجة لحالة "مجموعة") بصرف النظر عن العمود الذي
  وردا فيه، بدليل 78+ حركة فعلية دون أي استثناء معاكس.
  ⚠ استثناء على الاستثناء (تصحيح 2026-09-28، راجع _pair_rate): في حالة
  "شخصان" تحديداً، هذا التصنيف القسري لا يُستخدم لتحديد استحقاق نسبة
  "دراجة+دراجة" (0.125%) — ذاك يُحسم حصراً من العمود الخام الفعلي لكل
  من الشخصين (موزع دراجة/موزع دراجة 2). تحقّقنا رقمياً أن كريم هاشم أو
  مراد علوش حين يظهران بعمود سيارة خام (موزع السائق/مساعد) مع شريك، تبقى
  النسبة 0.25% لكل منهما كأي زوج مختلط عادي — رغم أن فئتهما "الرسمية"
  دراجة دوماً لأغراض حالتي منفرد/مجموعة. فقط حين يكون عمودهما الخام
  الفعلي "موزع دراجة" أو "موزع دراجة 2" فعلاً تصبح النسبة 0.125%.

آلية "بيد السيد": عدد لا بأس به من حركات القبض (خصوصاً كشوف تحصيل مجمّعة)
تصل بأعمدة الموزعين فارغة تماماً ("بدون")، أو بعمود سائق يحمل اسماً بديلاً
غير حقيقي (عبد الرزاق خرمة / محمد اغا) بدلاً من الموزع الفعلي. في هذه الحالات
النص الحقيقي للمستفيد(ين) موجود داخل عمود "البيان" بصيغة:
  "بيد السيد <اسم> إيصال ..."  أو  "بيد السيد <اسم1> + <اسم2> إيصال ..."
تم التحقق من هذه الآلية على 100+ حركة فعلية (كشوف تحصيل كاملة) بمطابقة تامة
مع شيت "تقرير نتيجة " المرجعي بعد تفعيلها؛ دونها كانت هذه الحركات تُفقد
بالكامل من الاحتساب (وهذا هو سبب "النتائج غير الصحيحة" التي أبلغ عنها المستخدم).

المرتجعات: خصم موحّد -0.5% لكل مشارك، بصرف النظر عن دوره أو عدد المشاركين
معه (تحقّق شامل بمئات الأمثلة دون أي استثناء). هذا مختلف عن وصف المستخدم
الحرفي الذي طلب تطبيق "نفس قواعد" النقدية (نسب متدرجة حسب العدد/الفئة) —
لكن بيانات "تقرير نتيجة " المرجعية أظهرت بوضوح نسبة ثابتة أبسط، وتم اعتماد
المرجع الفعلي بدل الوصف الشفهي بناءً على طلب المستخدم صراحة بالتحقق من
النتائج مقابل هذا الشيت.

استخدامات "البيان" — موثّقة صراحة لتبقى واضحة بلا لبس (طلب المستخدم تحديداً
التأكد من هذه النقطة، بعد ملاحظته أن فئة الموزع يجب ألا تُستنتج من نص البيان):
  1) استخراج اسم مشارك (آلية "بيد السيد" أعلاه) — فقط حين تصل كل أعمدة
     DIST_COLS فارغة ("بدون") أو تحمل اسماً بديلاً غير حقيقي (PLACEHOLDER_NAMES).
  2) اكتشاف عبارة "لا تخصم على أحد" (NO_DEDUCT_RE)، أو "تخصم على المندوب"
     (DEDUCT_FROM_REP_RE، تصحيح 2026-09-28) — كلتاهما تُصفّر عمولة الموزع
     على الحركة (الأولى: لا خصم من أحد إطلاقاً؛ الثانية: الخصم يقع على
     المندوب لا على الموزع). لا تخلط هذه بعبارة "تخصم على الموزع" (خصم
     طبيعي كامل، لا صلة لها بأي تصفير).
  البيان لا يُستخدم أبداً، وفي أي مسار بالكود، لتحديد فئة الموزع (سيارة/دراجة)
  ولا لتحديد عدد/هوية المشاركين حين تكون أعمدة DIST_COLS مكتملة — تلك تُحسم
  حصراً من عضوية العمود (أي عمود من الخمسة ورد فيه الاسم) وفق تأكيد المستخدم
  الصريح أن "عمود الاسم في أعلى الصف" (أي عناوين DIST_COLS نفسها) هو المصدر
  الحقيقي، لا نص البيان الحر. راجع _resolve_tier_and_source أدناه — لا يقرأ
  البيان إطلاقاً، فقط اسم العمود (role_col) الذي ورد فيه اسم المشارك.

عمود "فئة السائق" المخصص (DRIVER_TYPE_COL_CANDIDATES) — أُزيل بعد التأكيد:
  كان اجتهاداً سابقاً (تخميناً لعمود مخصص افتراضي مثل "نوع السائق" لم يُشاهَد
  فعلياً في أي ملف) قبل أن يؤكد المستخدم صراحة أن الأعمدة الخمسة DIST_COLS
  نفسها (موزع السائق/مساعد/دراجة/دراجة 2/استثناء) هي "العمود الذي يحمل الاسم
  في أعلى الصف" — أي أنها المصدر الحقيقي والوحيد لتحديد دور/فئة كل مشارك،
  وليست استنتاجاً غير مباشر يحتاج تأكيداً إضافياً من عمود آخر. أُزيل مسار
  الاستدلال الاجتهادي هذا (وليس فقط أُهمل) لسببين: (أ) لم يُعثر عليه في أي
  ملف فعلي رغم فحص عدة نسخ من "نقدية الموزعين"، و(ب) إبقاؤه كمسار احتياطي
  فعّال يحمل خطراً حقيقياً مطابقاً لما وقعنا فيه فعلاً مع عمود "الفئة" (الذي
  تبيّن أنه لتسوية فئات العملة الورقية لا فئة السائق) — أي عمود مستقبلي يحمل
  اسماً مشابهاً بالصدفة (مثال: "فئة السائق" لغرض آخر تماماً) قد يُقرأ خطأً
  ويُطغي صامتاً على الآلية الصحيحة المؤكدة (عضوية DIST_COLS). حذف المسار
  بدل إبقائه "احتياطياً غير مفعّل" يمنع هذا الخطر نهائياً بما يتفق مع مبدأ
  المشروع: لا نخمّن بصمت. إن ظهر مستقبلاً ملف فعلي بعمود فئة سائق مخصص حقاً،
  يُضاف حينها بعد التحقق الحرفي من اسمه على ذلك الملف تحديداً، لا قبل ذلك.

استبعادات مؤكدة (بلا عمولة، ولا تُحتسب ضمن أي إجمالي):
  - حركات "دفتر الأستاذ" التي يحتوي فيها عمود "الحساب المقابل" على كلمة
    "مستودع" (تحصيل من/إلى مستودع داخلي، وليس صيدلية) — بصرف النظر عن أي
    دور موزع مسجَّل على الحركة.
  - علامات غير-شخصية ظاهرة أحياناً في أعمدة الموزعين: "بيد المندوب" (حصّلها
    المندوب مباشرة، وليس موزعاً)، "درعا" (اسم مدينة/خط سير)، وأي قيمة تحتوي
    "مستودع" في اسم الموزع نفسه.
  ملاحظة: شيت "تقرير نتيجة " المرجعي يُبقي على قيم سالبة صغيرة (من المرتجعات)
  تحت هذه العلامات نفسها بدل استبعادها بالكامل؛ فرق الإجمالي الناتج عن هذا
  الاستبعاد المتعمّد صغير جداً (أقل من 0.3% من الإجمالي العام) وهو موثّق في
  شيت الملخص المُصدَّر بدل إخفائه.

دقة الاحتساب المتحقق منها: فرق إجمالي عام ~0.25% (وعلى مستوى كل موزع تقريباً
ضمن ±4%) مقارنة بشيت "تقرير نتيجة " المرجعي الكامل لشهر تموز 2026 (8221 حركة
نقدية + 869 حركة مرتجع). الفروقات المتبقية الصغيرة تعود لحالات نادرة جداً
(اختلاف تهجئة اسم غير مكتشف، أو حركة مجموعة من 4+ أشخاص غير موثقة).
"""
from __future__ import annotations

import difflib
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from typing import Optional

# ---------------------------------------------------------------- ثوابت ----

DIST_COLS = ["موزع السائق", "موزع مساعد", "موزع دراجة", "موزع دراجة 2", "موزع استثناء"]
CAR_TIER_COLS = {"موزع السائق", "موزع مساعد", "موزع استثناء"}
MOTO_TIER_COLS = {"موزع دراجة", "موزع دراجة 2"}

WAREHOUSE_MARKER = "مستودع"
NON_PERSON_MARKERS = {"بيد المندوب", "درعا", "ارض مستودع"}
# أسماء بديلة/غير حقيقية تظهر أحياناً في عمود الموزع بدل الاسم الفعلي؛
# الاسم الحقيقي يُستخرج حصراً من نص البيان ("بيد السيد ...") عند توفره.
PLACEHOLDER_NAMES = {"عبد الرزاق خرمة", "محمد اغا"}
# سائقو دراجات مسجَّلون أحياناً في عمود سائق السيارة سهواً — يُعاملان دوماً كفئة دراجة.
MOTO_NAME_OVERRIDES = {"كريم هاشم", "مراد علوش"}

# --- إصلاح: "لا تخصم على أحد" يجب أن يصفّر العمولة لا أن يُتجاهَل ---
# وردت هذه الملاحظة فعلياً 367 مرة في عمود "ملاحظات" بشيت "مرتجعات" (بصيغة
# "لا تخصم على احد" بلا همزة) في الملف المرجعي؛ الكود القديم لم يكن يقرأ عمود
# "ملاحظات" أصلاً فكان يخصم عمولة/خصم مرتجع طبيعياً رغم التعليمة الصريحة بعدم
# الخصم من أي أحد. النمط أدناه يغطي هذه الصيغة وصيغة "لا يخصم على أحد" بالهمزة.
NO_DEDUCT_RE = re.compile(r"لا\s*[تي]خصم\s*على\s*[أا]حد")

# ملاحظة أخرى مختلفة المعنى عن "لا تخصم على أحد" لكن بنفس الأثر على عمولة
# الموزع — اكتُشفت 2026-09-28 أثناء تدقيق فرق ~41 ل.س بلّغ عنه المستخدم على
# موزعَين (احمد الحسن، مصطفى زيتون): عبارة "تخصم على المندوب" تعني أن قيمة
# المرتجع تُخصم فعلاً، لكن من *المندوب* (البائع) لا من *الموزع* (ناقل
# التحصيل) — فبالنسبة لعمولة الموزع تحديداً يجب أن تكون صفراً لهذه الحركة،
# تماماً كأثر "لا تخصم على أحد" وإن اختلف السبب. تحقّق رقمي من حالتين
# فعليتين فقط بالملف المرجعي (367 حركة "لا تخصم على أحد" مقابل 2 فقط بهذه
# الصيغة): احمد الحسن/2230 ل.س ومصطفى زيتون/5950 ل.س — كلتاهما صفر بالمرجع
# رغم عدم ورود "لا تخصم على أحد" حرفياً. يُميَّز هذا صراحة عن "تخصم على
# الموزع" (11 حركة فعلية) التي تعني العكس تماماً وتُخصم طبيعياً 0.5% كاملة
# في المرجع — لذا النمط أدناه يشترط كلمة "المندوب" تحديداً ولا يطابق
# "الموزع" أبداً.
DEDUCT_FROM_REP_RE = re.compile(r"تخصم\s*على\s*المندوب")

# أسماء معروفة تظهر فقط عبر آلية "بيد السيد" (بلا أي سجل عمود خام لاستنتاج
# فئتها)، مع فئتها الموثّقة من شهر التحقق المرجعي. يُضاف إليها عند الحاجة.
SEED_TIER_ROSTER = {
    "امجد ابو طومان": "moto",
}
EXPLICIT_ALIASES = {
    "احمد ابو طومان": "امجد ابو طومان",
    "امجد أبو طومان": "امجد ابو طومان",
    "احمد أبو طومان": "امجد ابو طومان",
    "علاء الحسن": "علاء محمد حسن",
    "علاء حسن": "علاء محمد حسن",
}

BIYAD_RE = re.compile(r"بيد السيد (.+?)\s*إيصال")

RATE_ALONE_CAR = Decimal("0.004")
RATE_ALONE_MOTO = Decimal("0.0025")
RATE_PAIR = Decimal("0.0025")
# تصحيح 2026-09-28 (بلاغ مستخدم + تحقّق رقمي كامل مقابل ملف "نقدية الموزعين
# شهر 8" المرجعي — راجع _pair_rate أدناه وتوثيق أعلى الملف): زوج "دراجة+دراجة"
# (كلا المشاركين فئة moto) يُقسَم بينهما نصف نسبة الزوج العادية، لا نفس النسبة
# كاملة لكل منهما كما كان مطبَّقاً سابقاً.
RATE_PAIR_MOTO_MOTO = RATE_PAIR / Decimal(2)
RATE_GROUP_CAR = Decimal("0.005") / Decimal(3)
RATE_GROUP_MOTO = Decimal("0.0025") / Decimal(3)
RETURN_RATE = Decimal("-0.005")

REQUIRED_LEDGER_COLS = {"رقم السند", "البيان", "مدين", "دائن", "التاريخ", "موزع السائق"}
REQUIRED_RETURN_COLS = {"الفاتورة", "القيمة المؤجلة", "موزع السائق"}


# --------------------------------------------------------------- أدوات ----

def _clean(v) -> str:
    if v is None:
        return ""
    return str(v).strip()


def _to_decimal(v) -> Decimal:
    if v is None or v == "":
        return Decimal("0")
    if isinstance(v, Decimal):
        return v
    if isinstance(v, (int, float)):
        return Decimal(str(v))
    try:
        return Decimal(str(v).replace(",", "").strip())
    except (InvalidOperation, ValueError):
        return Decimal("0")


def _is_populated(v) -> bool:
    if v in (None, "", 0, "0"):
        return False
    if isinstance(v, str) and v.strip() in ("بدون", "0", ""):
        return False
    return True


def is_warehouse(name) -> bool:
    return WAREHOUSE_MARKER in str(name or "")


def _is_no_deduct(text) -> bool:
    return bool(NO_DEDUCT_RE.search(str(text or "")))


def _is_deduct_from_rep(text) -> bool:
    return bool(DEDUCT_FROM_REP_RE.search(str(text or "")))


def _find_header(all_rows, required_cols, max_scan=12):
    for idx in range(min(max_scan, len(all_rows))):
        row = all_rows[idx]
        if not row:
            continue
        cells = {str(_clean(c)) for c in row if c is not None}
        if required_cols.issubset(cells):
            return idx, {str(_clean(c)): i for i, c in enumerate(row) if c is not None}
    raise ValueError("تعذّر العثور على صف العناوين المطلوب في الملف.")


def _strip_al(tok: str) -> str:
    return tok[2:] if tok.startswith("ال") and len(tok) > 2 else tok


def _token_set(name: str) -> frozenset:
    return frozenset(_strip_al(t) for t in name.split())


class NameResolver:
    """يبني قائمة موزعين مرجعية ديناميكياً من الأسماء الفعلية الواردة في
    ملف الشهر نفسه (وليس من قائمة ثابتة مسبقاً)، ثم يوحّد أي اختلاف تهجئة
    بسيط (حرف "ال"، خطأ إملائي طفيف) على الاسم الأكثر تكراراً لكل شخص.
    هذا يسمح للوحدة بالعمل تلقائياً مع موزعين جدد كل شهر دون تعديل الكود.
    """

    def __init__(self):
        self._freq: Counter = Counter()
        self._canon_by_tokenset: dict[frozenset, str] = {}
        self._cache: dict[str, Optional[str]] = {}
        self._finalized = False

    def observe(self, raw_name: str):
        name = _clean(raw_name)
        if not name or name in NON_PERSON_MARKERS or name in PLACEHOLDER_NAMES or is_warehouse(name):
            return
        self._freq[name] += 1

    def finalize(self):
        # لكل مجموعة أسماء تتطابق بعد تجاهل "ال"، اختر الأكثر تكراراً كصيغة معتمدة.
        clusters: dict[frozenset, list[tuple[str, int]]] = defaultdict(list)
        for name, count in self._freq.items():
            clusters[_token_set(name)].append((name, count))
        for ts, variants in clusters.items():
            variants.sort(key=lambda x: -x[1])
            self._canon_by_tokenset[ts] = variants[0][0]
        self._finalized = True

    def resolve(self, raw_name: str) -> Optional[str]:
        name = _clean(raw_name)
        if not name:
            return None
        if name in self._cache:
            return self._cache[name]
        result = self._resolve_uncached(name)
        result = EXPLICIT_ALIASES.get(result, result) if result else EXPLICIT_ALIASES.get(name)
        self._cache[name] = result
        return result

    def _resolve_uncached(self, name: str) -> Optional[str]:
        if not self._finalized:
            self.finalize()
        if name in self._freq:
            return self._canon_by_tokenset[_token_set(name)]
        ts = _token_set(name)
        exact = self._canon_by_tokenset.get(ts)
        if exact:
            return exact
        # اسم واحد فقط (كنية مختصرة) ضمن اسم مركّب معروف
        subset_hits = [
            canon for cts, canon in self._canon_by_tokenset.items()
            if ts and ts.issubset(cts)
        ]
        if len(set(subset_hits)) == 1:
            return subset_hits[0]
        # خطأ إملائي طفيف: أقرب تطابق نصي
        candidates = list(self._canon_by_tokenset.values())
        close = difflib.get_close_matches(name, candidates, n=1, cutoff=0.72)
        if close:
            return close[0]
        return None

    def all_known_names(self):
        if not self._finalized:
            self.finalize()
        return sorted(set(self._canon_by_tokenset.values()))

    def resolve_with_kind(self, raw_name: str) -> tuple[Optional[str], str]:
        """مثل resolve()، لكن يرجع أيضاً نوع المطابقة: "exact" (الاسم كما
        ورد حرفياً بعمود خام سابقاً، أو نفس مجموعة الكلمات بترتيب/"ال"
        مختلف، أو عبر EXPLICIT_ALIASES الموثّق يدوياً مسبقاً)، أو "fuzzy"
        (اسم جزئي/كنية ضمن اسم مركّب معروف، أو أقرب تطابق نصي لخطأ إملائي
        طفيف غير موثّق مسبقاً) — أو "none" إن تعذّرت أي مطابقة.

        يُستخدم حصراً عند استخراج الأسماء من نص البيان (آلية "بيد السيد")
        لتمييز الحالات التي تحتاج تأكيداً يدوياً (طلب المستخدم 2026-09-28:
        "ممكن يختلف الاسم بحرف او اي شي تاني ... بدياك تعطيهم لون مختلف").
        resolve() العادية (المستخدمة لأسماء أعمدة DIST_COLS الخام) تبقى بلا
        تغيير — التمييز هنا مقصور على مصدر "البيان" فقط."""
        name = _clean(raw_name)
        if not name:
            return None, "none"
        if not self._finalized:
            self.finalize()
        if name in EXPLICIT_ALIASES:
            return EXPLICIT_ALIASES[name], "exact"
        if name in self._freq:
            canon = self._canon_by_tokenset[_token_set(name)]
            return EXPLICIT_ALIASES.get(canon, canon), "exact"
        ts = _token_set(name)
        exact = self._canon_by_tokenset.get(ts)
        if exact:
            return EXPLICIT_ALIASES.get(exact, exact), "exact"
        subset_hits = [
            canon for cts, canon in self._canon_by_tokenset.items()
            if ts and ts.issubset(cts)
        ]
        if len(set(subset_hits)) == 1:
            result = EXPLICIT_ALIASES.get(subset_hits[0], subset_hits[0])
            return result, "fuzzy"
        candidates = list(self._canon_by_tokenset.values())
        close = difflib.get_close_matches(name, candidates, n=1, cutoff=0.72)
        if close:
            result = EXPLICIT_ALIASES.get(close[0], close[0])
            return result, "fuzzy"
        return None, "none"


# ------------------------------------------------------------ التحليل ----

@dataclass
class Participant:
    name: str
    tier: str  # "car" | "moto"
    role_col: Optional[str] = None  # None يعني أنه استُخرج من نص البيان لا من عمود خام
    # مصدر تحديد الفئة (سيارة/دراجة) لهذا المشارك تحديداً — يُبقي القرار مرئياً
    # بدل إخفائه، خصوصاً حين لا يتوفر عمود فئة مخصص فيلجأ الكود للاستنتاج القديم.
    tier_source: str = ""
    # تصحيح 2026-09-28 (طلب المستخدم الصريح): "column" لمشارك ورد اسمه
    # حرفياً بأحد أعمدة DIST_COLS الخام. "exact"/"fuzzy" لمشارك استُخرج من
    # نص البيان (آلية "بيد السيد") فقط — "exact" إن طابق اسماً معروفاً
    # حرفياً (أو عبر EXPLICIT_ALIASES الموثّق يدوياً)، و"fuzzy" إن اعتمدت
    # المطابقة على اسم جزئي (كنية) أو تقارب إملائي (راجع
    # NameResolver.resolve_with_kind). يُستخدم فقط لتلوين/فرز حالات تحتاج
    # تأكيداً يدوياً بالتصدير — لا يغيّر الاحتساب إطلاقاً.
    match_kind: str = "column"


@dataclass
class LedgerRow:
    bayan: str
    debit: Decimal
    participants: list = field(default_factory=list)
    source: str = "دفتر الأستاذ"
    # True إذا وردت عبارة "لا تخصم على أحد" (أو ما شابه) في البيان — العمولة
    # تُصفَّر لكل المشاركين على هذه الحركة تحديداً، لكن الحركة تبقى ظاهرة كما هي.
    no_deduct: bool = False


@dataclass
class ReturnRow:
    bayan: str
    amount: Decimal
    participants: list = field(default_factory=list)
    source: str = "مرتجعات"
    # True إذا وردت عبارة "لا تخصم على أحد" في عمود "ملاحظات" (أو البيان) لهذه
    # الحركة — خصم المرتجع يُصفَّر لكل المشاركين، والحركة تبقى ظاهرة كما هي.
    no_deduct: bool = False
    note: str = ""


@dataclass
class ParseResult:
    collection_rows: list
    return_rows: list
    resolver: NameResolver
    warehouse_excluded_count: int = 0
    warehouse_excluded_amount: Decimal = Decimal("0")
    flagged_rows: list = field(default_factory=list)  # حركات تحتاج مراجعة يدوية (فئة/اسم غير معروف)
    excluded_marker_totals: dict = field(default_factory=dict)  # علامات غير-شخصية (بيد المندوب، درعا، ...)
    # عدّاد مصادر تحديد فئة السائق عبر كل المشاركين (عمود مخصص/استنتاج من عمود
    # الموزع/تكرار الشهر) — مرئي للتحقق بدل أن يبقى القرار مخفياً داخل الكود.
    tier_source_counts: dict = field(default_factory=dict)
    # حركات "لا تخصم على أحد" المصفَّرة عمداً — منفصلة عن flagged_rows لأنها
    # ليست حالة غامضة تحتاج مراجعة، بل استبعاد عمولة صريح موثّق بالبيان/الملاحظة.
    no_deduct_collection_count: int = 0
    no_deduct_collection_amount: Decimal = Decimal("0")
    no_deduct_return_count: int = 0
    no_deduct_return_amount: Decimal = Decimal("0")
    # تصحيح 2026-09-28 (طلب المستخدم الصريح، حالتان جديدتان):
    #  1) fuzzy_biyad_rows: حركات فيها مشارك استُخرج اسمه من نص البيان
    #     بمطابقة تقريبية فقط (كنية/خطأ إملائي طفيف) — تبقى مُحتسَبة
    #     بالعمولة كالمعتاد، لكن تُعلَّم بلون مختلف + شيت مراجعة منفصل
    #     ليتأكد المستخدم يدوياً من صحة المطابقة.
    #  2) unresolved_collection_rows / unresolved_return_rows: حركات لا
    #     يوجد لها أي مشارك معروف إطلاقاً — لا بعمود DIST_COLS خام ولا
    #     بنص البيان (لا تطابق بيد السيد ولا حتى تقريبي). سابقاً كانت هذه
    #     الحركات تُحذف صامتة بالكامل (بلا عمولة، بلا ظهور بأي شيت) — الآن
    #     تبقى ظاهرة بشيت مراجعة أحمر مخصص بدل الاختفاء الصامت (لا تُحتسب
    #     لأي موزع، إذ لا يوجد مشارك معروف يُنسب له المبلغ).
    fuzzy_biyad_rows: list = field(default_factory=list)
    unresolved_collection_rows: list = field(default_factory=list)
    unresolved_return_rows: list = field(default_factory=list)


def _extract_biyad_names(bayan: str, resolver: NameResolver) -> list[tuple[str, str]]:
    """يرجع [(الاسم المطابَق، نوع المطابقة)] — راجع resolve_with_kind. اسم
    واحد أو اسمان (مفصولان بـ"+") أو ثلاثة، كل واحد منهم يُقيَّم على حدة."""
    m = BIYAD_RE.search(bayan)
    if not m:
        return []
    raw = m.group(1)
    out = []
    for part in raw.split("+"):
        resolved, kind = resolver.resolve_with_kind(part)
        if resolved:
            out.append((resolved, kind))
    # إزالة التكرار (بالاسم) مع الحفاظ على الترتيب
    seen = set()
    result = []
    for nm, kind in out:
        if nm in seen:
            continue
        seen.add(nm)
        result.append((nm, kind))
    return result


def _resolve_tier_and_source(name: str, role_col: Optional[str]) -> tuple[str, str]:
    """يحدد فئة الموزع (سيارة/دراجة) ومصدر هذا التحديد. لا يقرأ نص البيان
    إطلاقاً — فقط اسم المشارك واسم عمود DIST_COLS الذي ورد فيه (role_col).

    ترتيب الأولوية:
      1) استثناء اسم مسجَّل (كريم هاشم/مراد علوش) — يبقى فوق كل شيء لأنه موثّق
         بـ 78+ حركة فعلية بلا استثناء معاكس (راجع توثيق أعلى الملف).
      2) عضوية عمود DIST_COLS الذي ورد فيه اسم المشارك فعلياً في هذا الصف —
         هذا هو المصدر الحقيقي والمؤكد صراحة من المستخدم ("العمود الذي يحمل
         الاسم في أعلى الصف"): موزع السائق/مساعد/استثناء -> فئة سيارة،
         موزع دراجة/دراجة 2 -> فئة دراجة. role_col=None فقط للمشاركين
         المُستخرَجين من "بيد السيد" حين لا عمود خام لهم أصلاً — عندها القرار
         يقع على resolve_tier (تكرار عمود الشهر) في المستدعي، وليس هنا.
    """
    if name in MOTO_NAME_OVERRIDES:
        return "moto", "استثناء اسم مسجَّل (دراجة دائماً)"
    if role_col is None:
        return "car", "افتراضي مؤقت (بيد السيد بلا تكرار شهر معروف)"
    return ("car" if role_col in CAR_TIER_COLS else "moto"), "عمود الموزع (DIST_COLS) — المصدر المؤكد"


def parse_distributor_file(file_obj) -> ParseResult:
    """يقرأ شيتي 'دفتر الأستاذ' و'مرتجعات' من نفس الملف المرفوع، ويحسب
    قائمة مشاركين موثوقة لكل حركة (مع تفعيل آلية 'بيد السيد' عند اللزوم)."""
    import openpyxl

    wb = openpyxl.load_workbook(file_obj, data_only=True, read_only=True)

    ledger_sheet = None
    returns_sheet = None
    for name in wb.sheetnames:
        if ledger_sheet is None and ("الأستاذ" in name or "استاذ" in name):
            ledger_sheet = name
        if returns_sheet is None and "مرتجع" in name:
            returns_sheet = name
    if ledger_sheet is None:
        raise ValueError("تعذّر العثور على شيت 'دفتر الأستاذ' داخل الملف.")

    ws = wb[ledger_sheet]
    rows = list(ws.iter_rows(values_only=True))
    header_idx, cols = _find_header(rows, REQUIRED_LEDGER_COLS)
    c_debit, c_date, c_bayan = cols["مدين"], cols["التاريخ"], cols["البيان"]
    c_account = cols.get("الحساب المقابل")
    dist_cols = {c: cols[c] for c in DIST_COLS if c in cols}

    raw_ledger_rows = []
    for row in rows[header_idx + 1:]:
        if not row or row[c_date] in (None, "", 0, "0"):
            continue
        debit = _to_decimal(row[c_debit])
        if debit <= 0:
            continue
        raw_ledger_rows.append(row)

    rrows = []
    rcols = {}
    r_header_idx = None
    c_ramount = c_rdate = None
    c_rnote = None
    if returns_sheet:
        ws2 = wb[returns_sheet]
        rrows_all = list(ws2.iter_rows(values_only=True))
        r_header_idx, rcols = _find_header(rrows_all, REQUIRED_RETURN_COLS)
        c_ramount = rcols["القيمة المؤجلة"]
        c_rcustomer = rcols.get("اسم الزبون")
        # عمود "ملاحظات" هو مصدر عبارة "لا تخصم على أحد" فعلياً في شيت المرتجعات
        # (367 حركة موثّقة في الملف المرجعي) — لم يكن الكود القديم يقرأه إطلاقاً.
        c_rnote = rcols.get("ملاحظات")
        for row in rrows_all[r_header_idx + 1:]:
            if not row:
                continue
            amt = _to_decimal(row[c_ramount])
            if amt == 0:
                continue
            rrows.append(row)

    # -------- بناء قائمة الأسماء المرجعية من كل الأعمدة الخام (الشيتين معاً) --------
    resolver = NameResolver()
    for row in raw_ledger_rows:
        for rc, idx in dist_cols.items():
            v = row[idx] if idx < len(row) else None
            if _is_populated(v):
                resolver.observe(v)
    for row in rrows:
        for rc in DIST_COLS:
            if rc in rcols:
                v = row[rcols[rc]]
                if _is_populated(v):
                    resolver.observe(v)
    resolver.finalize()

    def infer_tier(name: str) -> Optional[str]:
        if name in MOTO_NAME_OVERRIDES:
            return "moto"
        # ابحث عن الفئة الغالبة من الأعمدة الخام التي رصدها resolver
        # (نعيد فحص الأعمدة الخام هنا لأن NameResolver لا يحتفظ بالعمود)
        return _tier_freq.get(name)

    # فئة كل اسم بحسب العمود الأكثر تكراراً الذي ورد فيه (باستثناء حركات "بيد السيد"
    # التي تحمل اسماً بديلاً/فارغاً وقد تُضلّل الإحصاء)
    _tier_counts: dict[str, Counter] = defaultdict(Counter)
    for row in raw_ledger_rows:
        bayan = _clean(row[c_bayan])
        has_biyad = bool(BIYAD_RE.search(bayan))
        for rc, idx in dist_cols.items():
            v = row[idx] if idx < len(row) else None
            if not _is_populated(v):
                continue
            raw_nm = _clean(v)
            if raw_nm in NON_PERSON_MARKERS or raw_nm in PLACEHOLDER_NAMES or is_warehouse(raw_nm):
                continue
            nm = resolver.resolve(raw_nm) or raw_nm
            if has_biyad and nm in PLACEHOLDER_NAMES:
                continue
            _tier_counts[nm][rc] += 1
    _tier_freq: dict[str, str] = {}
    for nm, counter in _tier_counts.items():
        top_col, _ = counter.most_common(1)[0]
        _tier_freq[nm] = "car" if top_col in CAR_TIER_COLS else "moto"
    for nm, tier in SEED_TIER_ROSTER.items():
        _tier_freq.setdefault(nm, tier)

    def resolve_tier(name: str) -> Optional[str]:
        if name in MOTO_NAME_OVERRIDES:
            return "moto"
        return _tier_freq.get(name)

    # -------------------------------- تحصيل نقدي (دفتر الأستاذ) --------------------------------
    collection_rows: list[LedgerRow] = []
    flagged_rows: list[dict] = []
    excluded_marker_totals: dict[str, Decimal] = defaultdict(Decimal)
    warehouse_excluded_count = 0
    warehouse_excluded_amount = Decimal("0")
    tier_source_counts: Counter = Counter()
    no_deduct_collection_count = 0
    no_deduct_collection_amount = Decimal("0")
    fuzzy_biyad_rows: list[dict] = []
    unresolved_collection_rows: list[dict] = []

    for row in raw_ledger_rows:
        debit = _to_decimal(row[c_debit])
        bayan = _clean(row[c_bayan])
        account = _clean(row[c_account]) if c_account is not None else ""
        # ملاحظة تحقق 2026-08-31: تم فحص هذا الاستبعاد بعمق. الملف المرجعي
        # يحوي 6 حركات فعلية بهذا الشرط ("الحساب المقابل" يحتوي "مستودع"،
        # إجمالي مدين 695972 على 3 حسابات مستودع مختلفة). فحص شيت "تقرير
        # نتيجة " *بصيغه الخام* (بلا data_only) أظهر أن 5 من هذه الـ6 أعمدة
        # عمولتها (Q/R/S/T/U) مكتوبة كقيم ثابتة صفر (وليست صيغ) — أي أن مُعِد
        # الملف تعمّد تصفير عمولتها يدوياً، ما يؤكد أن قاعدة الاستبعاد
        # الأصلية صحيحة لـ5 من 6 حالات. الحالة السادسة فقط (سند 142153،
        # مدين=94470، سليم العبد، عمود دراجة) ظلّت صيغة حيّة "=D2925" لم
        # تُصفَّر، فتحتسب 236.175 — ما يفسّر فجوة سليم العبد -236.17 المتبقية
        # بالضبط. الأرجح أن هذا سهو فردي في إعداد الملف المرجعي (نسخ/لصق صفر
        # نُسي في هذا السطر بالذات) وليس استثناءً مقصوداً — لذلك أُبقيت قاعدة
        # الاستبعاد كما كانت (متوافقة مع 5/6 حالات مؤكَّدة)، وفجوة سليم العبد
        # تبقى موثَّقة وغير محلولة على مستوى الكود (أُبلغ المستخدم بها).
        #
        # تأكيد صريح من المستخدم 2026-08-31: بعد عرض هذا التحليل بالتفصيل
        # (رقم السند، البيان، والمقارنة مع الحالات الخمس المشابهة المُصفَّرة
        # يدوياً بملفهم)، أكّد المستخدم أن حركات التحصيل من حساب "مستودع"
        # (تحصيل داخلي وليس من صيدلية) لا يجب أن تُحسب لها عمولة إطلاقاً —
        # أي أن قاعدة الاستبعاد الحالية صحيحة، وفجوة سليم العبد (-236.17)
        # سببها خطأ فردي بملف المستخدم نفسه (سطر لم يُصفَّر مثل نظرائه)،
        # وليست خللاً بمنطقنا. لا حاجة لأي تعديل هنا.
        if is_warehouse(account):
            warehouse_excluded_count += 1
            warehouse_excluded_amount += debit
            continue

        raw_participants: list[Participant] = []
        saw_placeholder = False  # وُجد اسم بديل غير حقيقي بأحد الأعمدة (يحتاج استبداله من البيان)
        for rc, idx in dist_cols.items():
            v = row[idx] if idx < len(row) else None
            if not _is_populated(v):
                continue
            raw_nm = _clean(v)
            if raw_nm in NON_PERSON_MARKERS or is_warehouse(raw_nm):
                excluded_marker_totals[raw_nm] += debit  # إعلامي فقط، لا يُحتسب لأي موزع
                continue
            if raw_nm in PLACEHOLDER_NAMES:
                saw_placeholder = True
                continue  # سيُستبدل من نص البيان أدناه إن أمكن
            nm = resolver.resolve(raw_nm)
            if nm is None:
                flagged_rows.append({"reason": "اسم غير معروف", "bayan": bayan, "debit": debit, "name": raw_nm})
                continue
            tier, tier_source = _resolve_tier_and_source(nm, rc)
            tier_source_counts[tier_source] += 1
            raw_participants.append(Participant(name=nm, tier=tier, role_col=rc, tier_source=tier_source))

        # إصلاح 2026-08-31: آلية "بيد السيد" يجب أن تُفعَّل فقط حين توجد فعلاً
        # فجوة تحتاج سدّاً من البيان — إما (أ) كل أعمدة DIST_COLS فارغة تماماً
        # ("بدون")، أو (ب) أحد الأعمدة كان يحمل اسماً بديلاً غير حقيقي
        # (PLACEHOLDER_NAMES) يحتاج استبداله — تماماً كما هو موثّق أعلى الملف.
        # ليس كل مرة يذكر فيها البيان عبارة "بيد السيد" بصرف النظر عن محتوى
        # الأعمدة الخام. الكود القديم كان يشغّل الاستخراج دائماً ويضيف أي اسم
        # بيان غير موجود أصلاً بين المشاركين، حتى لو كان الصف يملك مشاركين
        # حقيقيين كاملين من الأعمدة الخام بلا أي عمود بديل (حالة فعلية
        # مؤكَّدة: صف بعمودي "موزع السائق"+"موزع مساعد" مكتملين باسمين
        # حقيقيين، وبيانه يذكر "بيد السيد <شخص ثالث غير مرتبط> + <أحد
        # الاثنين الموجودين>" — كان يُضاف الشخص الثالث كمشارك وهمي، محوّلاً
        # زوجاً حقيقياً (0.25% لكل منهما) إلى مجموعة ثلاثية وهمية). بالمقابل،
        # حالة مختلطة حقيقية (عمود بديل + عمود اسم حقيقي معاً بنفس الصف، مثل
        # "موزع السائق"=عبد الرزاق خرمة [بديل] و"موزع مساعد"=محمد دللول
        # [حقيقي]، والبيان "بيد السيد طارق سراقبي + محمد دللول") ما زالت
        # تعمل صح: raw_participants ليست فارغة (فيها محمد دللول) لكن
        # saw_placeholder=True فتُفعَّل آلية البيان وتُضاف طارق سراقبي فقط
        # (محمد دللول موجود أصلاً فلا يُكرَّر). تحقّق مباشر: تصحيح الحالة (أ)
        # وحدها كان يُصلح 8+ موزعين لكن يكسر 4 آخرين كانوا يعتمدون فعلاً على
        # هذه الحالة المختلطة (ب) — التمييز بينهما بعلم saw_placeholder صحّح
        # الاثنتين معاً دون التضحية بأي منهما.
        present_names = {p.name for p in raw_participants}
        if raw_participants and not saw_placeholder:
            extra_names = []
        else:
            biyad_names = _extract_biyad_names(bayan, resolver)
            extra_names = [(n, k) for n, k in biyad_names if n not in present_names]

        for nm, match_kind in extra_names:
            if nm in MOTO_NAME_OVERRIDES:
                tier, tier_source = "moto", "استثناء اسم مسجَّل (دراجة دائماً)"
            else:
                # لا عمود خام لهذا المشارك (استُخرج اسمه من البيان فقط) — الفئة
                # هنا تُستنتج من العمود الذي غلب على اسمه في بقية حركات الشهر
                # (resolve_tier)، وليس من نص البيان نفسه بأي شكل.
                tier, tier_source = resolve_tier(nm), "تكرار الشهر (بيد السيد، بلا عمود خام لهذا المشارك)"
            if tier is None:
                flagged_rows.append({"reason": "فئة غير معروفة (بيد السيد)", "bayan": bayan, "debit": debit, "name": nm})
                continue
            tier_source_counts[tier_source] += 1
            raw_participants.append(Participant(name=nm, tier=tier, role_col=None, tier_source=tier_source,
                                                  match_kind=match_kind))

        # تصحيح 2026-09-28 (الحالة الأولى، طلب المستخدم الصريح): مشارك
        # استُخرج اسمه من البيان بمطابقة تقريبية فقط (كنية/خطأ إملائي طفيف،
        # وليس تطابقاً حرفياً أو عبر EXPLICIT_ALIASES الموثّق) — يبقى
        # مُحتسَباً بالعمولة كالمعتاد، لكن الحركة بأكملها تُسجَّل هنا أيضاً
        # لتظهر بلون مختلف + شيت مراجعة منفصل بالتصدير ("مشاركون من البيان
        # بمطابقة تقريبية") ليتأكد المستخدم يدوياً من صحة المطابقة.
        fuzzy_names = [p.name for p in raw_participants if p.match_kind == "fuzzy"]
        if fuzzy_names:
            fuzzy_biyad_rows.append({
                "bayan": bayan, "debit": debit,
                "names": "، ".join(fuzzy_names),
                "all_names": "، ".join(p.name for p in raw_participants),
            })

        if not raw_participants:
            # تصحيح 2026-09-28 (الحالة الثانية، طلب المستخدم الصريح): لا يوجد
            # أي مشارك معروف إطلاقاً — لا بعمود DIST_COLS خام ولا حتى بمطابقة
            # تقريبية من نص البيان. سابقاً كانت هذه الحركة تُحذف صامتة بالكامل
            # (`continue` بلا أي تسجيل) — الآن تبقى ظاهرة بشيت مراجعة أحمر
            # مخصص ("حركات بلا أي موزع معروف") بدل الاختفاء الصامت. لا تُحتسب
            # لأي موزع (لا يوجد من يُنسب له المبلغ).
            unresolved_collection_rows.append({"bayan": bayan, "debit": debit})
            continue
        if len(raw_participants) > 3:
            flagged_rows.append({
                "reason": f"عدد مشاركين غير مسبوق ({len(raw_participants)}) — لا بيانات مرجعية لهذه الحالة",
                "bayan": bayan, "debit": debit, "name": "، ".join(p.name for p in raw_participants),
            })

        # إصلاح: "لا تخصم على أحد" في نص البيان يجب أن يصفّر العمولة على هذه
        # الحركة تحديداً — لا تُحذف الحركة ولا تُستبعد من التقرير، فقط تُعلَّم
        # وتُصفَّر عمولتها (راجع compute_collection_commission وflagged_rows).
        no_deduct = _is_no_deduct(bayan)
        if no_deduct:
            no_deduct_collection_count += 1
            no_deduct_collection_amount += debit
            flagged_rows.append({
                "reason": "لا تخصم على أحد — عمولة مصفَّرة عمداً بناءً على نص البيان",
                "bayan": bayan, "debit": debit, "name": "، ".join(p.name for p in raw_participants),
            })

        collection_rows.append(LedgerRow(bayan=bayan, debit=debit, participants=raw_participants, no_deduct=no_deduct))

    # -------------------------------- مرتجعات --------------------------------
    return_rows: list[ReturnRow] = []
    no_deduct_return_count = 0
    no_deduct_return_amount = Decimal("0")
    unresolved_return_rows: list[dict] = []
    if returns_sheet:
        for row in rrows:
            amt = _to_decimal(row[c_ramount])
            bayan_val = row[rcols["الفاتورة"]] if "الفاتورة" in rcols else ""
            bayan = _clean(bayan_val)
            note = _clean(row[c_rnote]) if c_rnote is not None and c_rnote < len(row) else ""
            parts: list[Participant] = []
            for rc in DIST_COLS:
                if rc not in rcols:
                    continue
                v = row[rcols[rc]]
                if not _is_populated(v):
                    continue
                raw_nm = _clean(v)
                if raw_nm in NON_PERSON_MARKERS or raw_nm in PLACEHOLDER_NAMES or is_warehouse(raw_nm):
                    excluded_marker_totals[raw_nm] += amt * RETURN_RATE
                    continue
                nm = resolver.resolve(raw_nm)
                if nm is None:
                    flagged_rows.append({"reason": "اسم غير معروف (مرتجع)", "bayan": bayan, "debit": amt, "name": raw_nm})
                    continue
                tier, tier_source = _resolve_tier_and_source(nm, rc)
                tier_source_counts[tier_source] += 1
                parts.append(Participant(name=nm, tier=tier, role_col=rc, tier_source=tier_source))
            if not parts:
                # تصحيح 2026-09-28: نفس إصلاح الحالة الثانية أعلاه (تحصيل
                # نقدي)، مطبَّق هنا للمرتجعات أيضاً للاتساق — حركة مرتجع بلا
                # أي مشارك معروف بأي عمود DIST_COLS لم تعد تُحذف صامتة؛
                # تبقى ظاهرة بشيت "حركات بلا أي موزع معروف" (أحمر).
                unresolved_return_rows.append({"bayan": bayan, "debit": amt})
                continue

            # إصلاح: عمود "ملاحظات" (والبيان احتياطاً) يُقرأ فعلياً الآن — سابقاً
            # لم يكن يُقرأ إطلاقاً فكانت هذه الحركات تُخصم منها 0.5% رغم التعليمة
            # الصريحة بعدم الخصم من أي أحد (367 حركة موثّقة بالملف المرجعي).
            is_literal_no_deduct = _is_no_deduct(note) or _is_no_deduct(bayan)
            # تصحيح 2026-09-28: "تخصم على المندوب" (راجع DEDUCT_FROM_REP_RE
            # أعلاه) — نفس الأثر على عمولة الموزع (صفر)، لسبب مختلف.
            is_deduct_from_rep = _is_deduct_from_rep(note) or _is_deduct_from_rep(bayan)
            no_deduct = is_literal_no_deduct or is_deduct_from_rep
            if no_deduct:
                no_deduct_return_count += 1
                no_deduct_return_amount += amt
                reason = (
                    "لا تخصم على أحد — خصم المرتجع مصفَّر عمداً بناءً على ملاحظة الحركة"
                    if is_literal_no_deduct else
                    "تخصم على المندوب لا على الموزع — خصم المرتجع مصفَّر عن هذا الموزع "
                    "بناءً على ملاحظة الحركة (يتحمّله المندوب لا الموزع)"
                )
                flagged_rows.append({
                    "reason": reason,
                    "bayan": bayan, "debit": amt, "name": "، ".join(p.name for p in parts),
                })

            return_rows.append(ReturnRow(bayan=bayan, amount=amt, participants=parts, no_deduct=no_deduct, note=note))

    return ParseResult(
        collection_rows=collection_rows,
        return_rows=return_rows,
        resolver=resolver,
        warehouse_excluded_count=warehouse_excluded_count,
        warehouse_excluded_amount=warehouse_excluded_amount,
        flagged_rows=flagged_rows,
        excluded_marker_totals=dict(excluded_marker_totals),
        tier_source_counts=dict(tier_source_counts),
        no_deduct_collection_count=no_deduct_collection_count,
        no_deduct_collection_amount=no_deduct_collection_amount,
        no_deduct_return_count=no_deduct_return_count,
        no_deduct_return_amount=no_deduct_return_amount,
        fuzzy_biyad_rows=fuzzy_biyad_rows,
        unresolved_collection_rows=unresolved_collection_rows,
        unresolved_return_rows=unresolved_return_rows,
    )


# --------------------------------------------------------- الاحتساب ----

def _pair_rate(parts: list) -> Decimal:
    """معدل حركة حالة "شخصان" (n=2). تصحيح 2026-09-28 (بلاغ مستخدم صريح:
    "لما عم يكون الموزع على دراجة وفي معو موزع تاني دراجة لازم هون النسبة
    تنقسم على 2") — تحقّقنا رقمياً من ملف "نقدية الموزعين شهر 8" المرجعي
    (شيت "تقرير"، عمود العدد=2، بمقارنة عمود العمولة الفعلي لكل مشارك ÷
    المبلغ): 4345 حركة "سيارة+سيارة" و531 حركة مختلطة "سيارة+دراجة" — في
    كلتيهما 0.25% (RATE_PAIR) لكل مشارك بلا أي استثناء، بينما 119 حركة
    "دراجة+دراجة" (كلا المشاركين فئة moto) جميعها 0.125% لكل مشارك بالضبط
    (أي نصف RATE_PAIR) بلا أي استثناء أيضاً.

    مهم — الشرط هنا هو **عمود الخام** (role_col ضمن MOTO_TIER_COLS: "موزع
    دراجة"/"موزع دراجة 2") لا حقل p.tier العام: اكتشفنا أثناء التحقق أن
    "كريم هاشم" و"مراد علوش" (أسماء MOTO_NAME_OVERRIDES التي p.tier لها
    دوماً "moto" بصرف النظر عن العمود، لأغراض حالتي "منفرد"/"مجموعة")
    يظهران أحياناً في عمود سيارة خام (موزع السائق/مساعد) مع شريك آخر —
    وفي هذه الحالات كانت نسبة المرجع 0.25% (زوج مختلط فعلياً حسب العمود
    الخام، رغم أن tier المُعاد تصنيفه يقول "moto" للاثنين). فقط حين يكون
    العمودان الخامان الفعليان لكلا الشخصين هما "موزع دراجة"/"موزع دراجة 2"
    تحديداً (كحالة سليم العبد+يوسف شروف، وحالة كريم هاشم حين يظهر فعلاً
    بعمود "موزع دراجة" مع يوسف شروف بعمود "موزع دراجة 2") تكون النسبة
    0.125%. مشارك مستخرَج من البيان بلا عمود خام (role_col=None) لا يُعامَل
    كزوج دراجتين هنا لعدم وجود دليل مرجعي على ذلك — يبقى على 0.25%
    الافتراضية."""
    if all(getattr(p, "role_col", None) in MOTO_TIER_COLS for p in parts):
        return RATE_PAIR_MOTO_MOTO
    return RATE_PAIR


def compute_collection_commission(collection_rows: list[LedgerRow]) -> dict[str, Decimal]:
    """يوزّع عمولة التحصيل النقدي حسب عدد المشاركين وفئة كل منهم (راجع
    التوثيق في أعلى الملف لتفصيل النسب المتحقق منها)."""
    out: dict[str, Decimal] = defaultdict(Decimal)
    for row in collection_rows:
        # إصلاح: "لا تخصم على أحد" — الحركة تبقى في collection_rows (مرئية في
        # شيت "تفصيل حركات التحصيل" وشيت "حركات للمراجعة") لكن عمولتها = 0
        # لكل المشاركين، بدل أن تُحتسب طبيعياً كما كان يحدث سابقاً.
        if row.no_deduct:
            continue
        parts = row.participants
        n = len(parts)
        debit = row.debit
        if n == 1:
            p = parts[0]
            rate = RATE_ALONE_CAR if p.tier == "car" else RATE_ALONE_MOTO
            out[p.name] += debit * rate
        elif n == 2:
            rate = _pair_rate(parts)
            for p in parts:
                out[p.name] += debit * rate
        else:  # 3 فأكثر: فئة كل شخص على حدة، بقسمة ثابتة على 3
            for p in parts:
                rate = RATE_GROUP_CAR if p.tier == "car" else RATE_GROUP_MOTO
                out[p.name] += debit * rate
    return dict(out)


def compute_return_commission(return_rows: list[ReturnRow]) -> dict[str, Decimal]:
    """خصم موحّد 0.5% من كل مشارك في حركة المرتجع، بصرف النظر عن دوره أو
    عدد المشاركين معه (راجع التوثيق في أعلى الملف)."""
    out: dict[str, Decimal] = defaultdict(Decimal)
    for row in return_rows:
        # إصلاح: "لا تخصم على أحد" — نفس المنطق أعلاه: الحركة تبقى ظاهرة في
        # return_rows، لكن خصمها = 0 لكل المشاركين بدل تطبيق RETURN_RATE.
        if row.no_deduct:
            continue
        for p in row.participants:
            out[p.name] += row.amount * RETURN_RATE
    return dict(out)


def compute_totals(parsed: ParseResult) -> dict:
    collection = compute_collection_commission(parsed.collection_rows)
    returns = compute_return_commission(parsed.return_rows)
    names = set(collection) | set(returns)
    totals = {nm: collection.get(nm, Decimal("0")) + returns.get(nm, Decimal("0")) for nm in names}
    return {
        "totals": totals,
        "collection_commission": collection,
        "return_commission": returns,
        "collection_total": sum(collection.values(), Decimal("0")),
        "return_total": sum(returns.values(), Decimal("0")),
        "grand_total": sum(totals.values(), Decimal("0")),
    }


# ------------------------------------------ تفصيل كل موزع حسب "الحالة" ----
# طلب المستخدم صراحة: "تفصيل كل موزع منفرداً مع الربح المالي لكل حالة (منفرد/
# مع غيره) والعمولة لكل حالة" — بالإضافة إلى الإجمالي الحالي (لا بديلاً عنه).
# هذا القسم لا يغيّر أي رقم موجود مسبقاً؛ فقط يعيد توزيع نفس عمولة كل موزع على
# "حالة" الحركة التي كسبها فيها، باستخدام نفس النسب المتحقق منها أعلاه دون أي
# تعديل عليها. مجموع عمولة كل الحالات لكل موزع = عمولته الإجمالية تماماً
# (السطر السالب/الموجب لا يُقرَّب ولا يُهمَل — Decimal حصراً، بلا float).

SITUATION_ALONE = "منفرد"
SITUATION_PAIR = "مع شخص آخر (اثنان)"
SITUATION_GROUP = "مجموعة (3 فأكثر)"


def _situation_for(n: int) -> str:
    if n == 1:
        return SITUATION_ALONE
    if n == 2:
        return SITUATION_PAIR
    return SITUATION_GROUP


def compute_collection_situation_breakdown(
    collection_rows: list[LedgerRow],
) -> dict[str, dict[str, dict]]:
    """يبني لكل موزع تفصيلاً حسب حالة الحركة (منفرد/مع شخص آخر/مجموعة):
    عدد الحركات، إجمالي المبلغ (مدين)، والعمولة المكتسبة في تلك الحالة تحديداً
    — بنفس نسب compute_collection_commission ذاتها دون أي تغيير.
    حركات "لا تخصم على أحد" تُستبعد هنا تماماً كما في compute_collection_commission
    (عمولتها صفر ولا تُحتسب ضمن أي موزع أصلاً) حتى يبقى مجموع عمولة الحالات لكل
    موزع مطابقاً تماماً لعمولته الإجمالية في compute_collection_commission.

    الشكل: {اسم الموزع: {الحالة: {"count": عدد, "amount": مجموع المبلغ,
                                    "commission": مجموع العمولة}}}
    """
    out: dict[str, dict[str, dict]] = defaultdict(
        lambda: {
            s: {"count": 0, "amount": Decimal("0"), "commission": Decimal("0")}
            for s in (SITUATION_ALONE, SITUATION_PAIR, SITUATION_GROUP)
        }
    )
    for row in collection_rows:
        if row.no_deduct:
            continue
        parts = row.participants
        n = len(parts)
        debit = row.debit
        situation = _situation_for(n)
        if n == 1:
            p = parts[0]
            rate = RATE_ALONE_CAR if p.tier == "car" else RATE_ALONE_MOTO
            bucket = out[p.name][situation]
            bucket["count"] += 1
            bucket["amount"] += debit
            bucket["commission"] += debit * rate
        elif n == 2:
            rate = _pair_rate(parts)
            for p in parts:
                bucket = out[p.name][situation]
                bucket["count"] += 1
                bucket["amount"] += debit
                bucket["commission"] += debit * rate
        else:
            for p in parts:
                rate = RATE_GROUP_CAR if p.tier == "car" else RATE_GROUP_MOTO
                bucket = out[p.name][situation]
                bucket["count"] += 1
                bucket["amount"] += debit
                bucket["commission"] += debit * rate
    return {name: situations for name, situations in out.items()}


def compute_return_situation_breakdown(
    return_rows: list[ReturnRow],
) -> dict[str, dict[str, dict]]:
    """نفس فكرة compute_collection_situation_breakdown، لكن لجانب المرتجعات.
    مهم: نسبة المرتجع (RETURN_RATE) ثابتة -0.5% بصرف النظر عن الحالة (راجع
    توثيق أعلى الملف) — أي أن هذا التفصيل لا يكشف نسباً مختلفة حسب الحالة هنا
    (كما في التحصيل)، بل يوضّح فقط توزّع عدد/مبلغ/خصم المرتجعات على كل حالة
    لكل موزع للشفافية، تماشياً مع طلب المستخدم تغطية الحالتين معاً."""
    out: dict[str, dict[str, dict]] = defaultdict(
        lambda: {
            s: {"count": 0, "amount": Decimal("0"), "commission": Decimal("0")}
            for s in (SITUATION_ALONE, SITUATION_PAIR, SITUATION_GROUP)
        }
    )
    for row in return_rows:
        if row.no_deduct:
            continue
        n = len(row.participants)
        situation = _situation_for(n)
        for p in row.participants:
            bucket = out[p.name][situation]
            bucket["count"] += 1
            bucket["amount"] += row.amount
            bucket["commission"] += row.amount * RETURN_RATE
    return {name: situations for name, situations in out.items()}


# --------------------------------------------- تفصيل كل موزع حسب دوره/حالته ----
# طلب المستخدم الصريح 2026-09-28: "بالنسبة لفيشة كل موزع لحال لازم يعطيني
# توتال التحصيل لكل حالة كان فيها سواء سائق سيارة أو أيا شي تاني ونسبة كل
# حالة من الحالات" — هذا بُعد مختلف تماماً عن "الحالة" أعلاه (منفرد/مع شخص
# آخر/مجموعة، حسب عدد المشاركين بالحركة): هنا "الحالة" تعني الدور/العمود
# الذي ظهر فيه الموزع فعلياً بكل حركة (سائق السيارة/مساعد/سائق الدراجة/
# دراجة 2/استثناء)، أو "من نص البيان" حين لا عمود خام له (آلية بيد السيد).
# لا يغيّر أي رقم موجود مسبقاً — فقط إعادة توزيع لنفس عمولة/تحصيل كل موزع
# حسب دوره الفعلي بكل حركة، بنفس النسب المتحقق منها أعلاه دون أي تعديل.
ROLE_LABELS = {
    "موزع السائق": "سائق السيارة",
    "موزع مساعد": "مساعد السائق",
    "موزع دراجة": "سائق الدراجة",
    "موزع دراجة 2": "سائق الدراجة (2)",
    "موزع استثناء": "استثناء (فئة سيارة)",
}
ROLE_FROM_BAYAN_LABEL = "من نص البيان (بلا عمود خام — بيد السيد)"
ROLE_ORDER = [*ROLE_LABELS.values(), ROLE_FROM_BAYAN_LABEL]


def _role_label(role_col: Optional[str]) -> str:
    if role_col is None:
        return ROLE_FROM_BAYAN_LABEL
    return ROLE_LABELS.get(role_col, role_col)


def compute_collection_role_breakdown(
    collection_rows: list[LedgerRow],
) -> dict[str, dict[str, dict]]:
    """يبني لكل موزع تفصيلاً حسب دوره/حالته الفعلية بكل حركة (سائق السيارة/
    مساعد/سائق الدراجة/دراجة 2/استثناء/من نص البيان) — عدد الحركات، إجمالي
    المبلغ، والعمولة المكتسبة بهذا الدور تحديداً، ونسبته الفعلية (العمولة ÷
    المبلغ). النسبة هنا "فعلية" (مُشتقّة من الأرقام) لا نسبة رسمية واحدة
    ثابتة لكل دور، لأن النسبة الحقيقية تعتمد أيضاً على عدد المشاركين بالحركة
    نفسها لا على الدور وحده (راجع جدول النسب أعلى الملف) — فقد يظهر نفس
    الدور بأكثر من نسبة فعلية إن اختلف عدد المشاركين بين حركاته. المجموع عبر
    كل الأدوار لكل موزع = عمولته الإجمالية تماماً في compute_collection_commission
    (بلا أي تغيير على الاحتساب نفسه، فقط إعادة عرض)."""
    out: dict[str, dict[str, dict]] = defaultdict(lambda: defaultdict(
        lambda: {"count": 0, "amount": Decimal("0"), "commission": Decimal("0")}
    ))
    for row in collection_rows:
        if row.no_deduct:
            continue
        parts = row.participants
        n = len(parts)
        debit = row.debit
        if n == 1:
            p = parts[0]
            rate = RATE_ALONE_CAR if p.tier == "car" else RATE_ALONE_MOTO
            bucket = out[p.name][_role_label(p.role_col)]
            bucket["count"] += 1
            bucket["amount"] += debit
            bucket["commission"] += debit * rate
        elif n == 2:
            rate = _pair_rate(parts)
            for p in parts:
                bucket = out[p.name][_role_label(p.role_col)]
                bucket["count"] += 1
                bucket["amount"] += debit
                bucket["commission"] += debit * rate
        else:
            for p in parts:
                rate = RATE_GROUP_CAR if p.tier == "car" else RATE_GROUP_MOTO
                bucket = out[p.name][_role_label(p.role_col)]
                bucket["count"] += 1
                bucket["amount"] += debit
                bucket["commission"] += debit * rate
    return {name: dict(roles) for name, roles in out.items()}


def compute_return_role_breakdown(
    return_rows: list[ReturnRow],
) -> dict[str, dict[str, dict]]:
    """نفس فكرة compute_collection_role_breakdown لجانب المرتجعات — نسبة
    المرتجع ثابتة -0.5% بصرف النظر عن الدور (كما في compute_return_situation_breakdown)،
    فهذا التفصيل يوضّح فقط توزّع عدد/مبلغ/خصم المرتجعات حسب دور كل موزع."""
    out: dict[str, dict[str, dict]] = defaultdict(lambda: defaultdict(
        lambda: {"count": 0, "amount": Decimal("0"), "commission": Decimal("0")}
    ))
    for row in return_rows:
        if row.no_deduct:
            continue
        for p in row.participants:
            bucket = out[p.name][_role_label(p.role_col)]
            bucket["count"] += 1
            bucket["amount"] += row.amount
            bucket["commission"] += row.amount * RETURN_RATE
    return {name: dict(roles) for name, roles in out.items()}


# ------------------------------------------------- توافق مع النسخة القديمة ----
# أُبقيت هذه الدالة لأي كود قديم قد يستدعيها مباشرة؛ الاستخدام الموصى به هو
# parse_distributor_file() أعلاه الذي يقرأ الشيتين معاً بمنطق أدق.

def parse_distributor_ledger(file_obj) -> list[dict]:
    parsed = parse_distributor_file(file_obj)
    out = []
    for row in parsed.collection_rows:
        participants = {p.role_col or f"بيد السيد ({p.name})": p.name for p in row.participants}
        out.append({"debit": row.debit, "participants": participants, "bayan": row.bayan})
    return out
