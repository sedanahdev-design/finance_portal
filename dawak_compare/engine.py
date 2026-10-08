"""محرك مطابقة دواك (الفكرة السادسة).

ملف "مشروع دواك" هو دفتر أستاذ مقسّم لكل صيدلية على حدة (كل صيدلية لها
صف عنوان فرعي، تليه حركات "بون" (حسم يُخصم/مدين) و"مرتجع وهمي" (رد الحسم/
دائن)). الصيدلية "مطابقة" إذا كان إجمالي البون = إجمالي المرتجع الوهمي
لها (أي أن كل حسم مُنح تم ترحيله وعكسه بشكل صحيح). النظام المصدر نفسه
أحياناً يضع علامة "[غير مطابق]" على رصيد الصيدلية — نحسب مطابقتنا
الخاصة بشكل مستقل، ونعرض علامة المصدر كذلك للمقارنة.

ملف "كشف حساب هبة" هو حساب إجمالي (وليس مفصّلاً لكل صيدلية) بين مستودع
هبة ومشروع دواك؛ نعرض إجمالياته (مدين/دائن/الرصيد) كمقارنة عامة مكمّلة،
ونحتفظ أيضاً بكل حركة منه على حدة (تاريخ/مبلغ) لاستخدامها في مطابقة
الحركات أدناه.

مطابقة الحركات بين دواك وهبة (إضافة لاحقة):
    بالإضافة لمطابقة كل صيدلية داخلياً (بون = مرتجع وهمي)، نطابق أيضاً كل
    حركات دواك (مسطّحة من كل الصيدليات) مع حركات كشف حساب هبة، بنفس أسلوب
    مطابقة هبة-سدانة (الفكرة الأولى): تجميع حسب المبلغ الدقيق ثم مقابلة
    بالتسلسل. أي حركة تبقى بلا مقابل ضمن مجموعة مبلغها تخضع لفحص ثانوي:
    نبحث في *كامل* حركات الطرف الآخر (حتى المُستخدمة أصلاً بمقابلة أخرى)
    عن نفس المبلغ بأي تاريخ. إن وُجدت لا تُصنَّف "فرق" بل "موجود بتاريخ
    مختلف" مع عرض التاريخين معاً؛ فقط إن لم يوجد المبلغ إطلاقاً تُصنَّف
    "فرق حقيقي". الهدف عدم إخفاء أي معلومة عن المستخدم بصمت.

مطابقة حسب "مركز الكلفة" (تصحيح 2026-09-30، طلب المستخدم الصريح):
    ملف "كشف حساب هبة" يحمل عمود "مركز الكلفة" يُسنِد كل حركة فيه إلى
    صيدلية/مستودع بعينه من ملف مشروع دواك — لكن التسمية غالباً لا تُطابق
    حرفياً اسم الحساب الفرعي بملف دواك. مثال حقيقي من ملف مرجعي فعلي
    (طلب المستخدم توضيحه بالضبط): حساب دواك الفرعي "1209014-مستودع سدانة-
    صناعة" يُسجَّل بملف هبة تحت مركز الكلفة "مستودع الصناعة" فقط (بلا كلمة
    "سدانة")؛ وأحياناً يكون مركز الكلفة اسم صيدلية بعينها (مثال: "صيدلية
    هناء بطحيش-كفرسوسة" يقابل حساب دواك "12011303-صيدلية هناء بطحيش -
    كفرسوسة"، بفارق شرطة/مسافة بسيط). المطابقة الحرفية السابقة (لا وجود لها
    أصلاً قبل هذا التصحيح) كانت ستفشل بهذه الفروقات، وهو ما بلّغ عنه
    المستخدم صراحة: "الفرق بس 7" لصيدلية هناء بطحيش لم يكن في الحقيقة
    ناتجاً عن أي مطابقة مع هبة إطلاقاً، بل هو فرق "بون - مرتجع وهمي" الداخلي
    بملف دواك وحده (طرح مدين من دائن **بنفس الملف**، بلا أي مقارنة حقيقية
    مع هبة) — بالضبط كما وصف المستخدم المشكلة.

    الحل: مطابقة تقريبية بتداخل الكلمات (بعد تطبيع الشرطات كفواصل كلمات،
    وتجريد بادئة "ال" من كل كلمة، وتوحيد الألف بأشكالها) بين نص "مركز
    الكلفة" واسم كل صيدلية/حساب فرعي بملف دواك — إن كانت كل كلمات الطرف
    الأقصر (بعد التطبيع) موجودة ضمن كلمات الطرف الأطول تُعتبَر مطابقة واثقة
    (تحقق فعلي: نتيجة تطابق كاملة 1.0 لكلا المثالين أعلاه، مقابل 0.0 مع أي
    صيدلية أخرى غير معنية). بعد الإسناد، نُجمِّع حركات هبة حسب الحساب
    الفرعي المُطابَق بدواك، ونقارن **بشكل تبادلي** (نفس منطق الاتجاهين في
    مطابقة الدفعات أعلاه: مدين طرف = دائن الطرف الآخر): دائن دواك للحساب
    ضد مدين هبة المطابق له، ومدين دواك ضد دائن هبة المطابق له (تحقق فعلي
    على الملف المرجعي: دائن دواك لحساب "مستودع سدانة- صناعة" = 105200.00
    بالضبط = مدين هبة لمركز الكلفة "مستودع الصناعة" = 105200.00 — تطابق
    تام، يثبت صحة اتجاه المقارنة). أي حساب فرعي بدواك ليس له أي حركة هبة
    مطابقة يُعرَض بوضوح بحالة مستقلة "لا توجد حركات مقابلة عند هبة" (لا
    "غير مطابق" المُضلِّلة، فهذا غياب بيانات لا فرق رقمي). وأي حركة هبة
    تحمل مركز كلفة لم نجد له أي حساب فرعي مطابق واثق بدواك تُعرَض في شيت
    مستقل للمراجعة اليدوية بدل إسقاطها بصمت.
"""

import re
from collections import defaultdict
from datetime import date, datetime
from decimal import Decimal

import openpyxl

HEADER_SIGNATURE = {"رقم السند", "مدين", "دائن", "التاريخ"}
STOP_MARKERS = {"المجموع", "الرصيد النهائي"}
SKIP_MARKERS = {"الرصيد السابق"}


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


def _to_date(v):
    """يحوّل قيمة تاريخ (كائن تاريخ/وقت جاهز، أو نص بصيغة يوم-شهر-سنة) إلى date.
    يعيد None إن تعذّرت القراءة، دون رفع استثناء يوقف كامل عملية المطابقة."""
    if v is None or v == "":
        return None
    if isinstance(v, datetime):
        return v.date()
    if isinstance(v, date):
        return v
    s = str(v).strip()
    parts = s.replace("/", "-").split("-")
    if len(parts) != 3:
        return None
    try:
        day, month, year = (int(p) for p in parts)
        if year < 100:
            year += 2000
        return date(year, month, day)
    except (ValueError, TypeError):
        return None


def parse_dawak_project(file_obj, tolerance=Decimal("1")):
    """يقرأ ملف مشروع دواك ويعيد قائمة صيدليات، كل واحدة بحركاتها ومطابقتها."""
    wb = openpyxl.load_workbook(file_obj, data_only=True, read_only=True)
    ws = wb[wb.sheetnames[0]]
    all_rows = list(ws.iter_rows(values_only=True))
    wb.close()

    header_idx = header = None
    for i, row in enumerate(all_rows):
        cells = {str(_clean(c)) for c in row if c is not None}
        if HEADER_SIGNATURE.issubset(cells):
            header_idx, header = i, [str(_clean(c)) for c in row]
            break
    if header_idx is None:
        raise ValueError("لم يتم العثور على صف العناوين المتوقع داخل ملف مشروع دواك.")

    col = {name: header.index(name) for name in header if name}

    def get(row, name):
        idx = col.get(name)
        if idx is None or idx >= len(row):
            return None
        return row[idx]

    pharmacies = []
    current = None
    for row in all_rows[header_idx + 1:]:
        if row is None or all(c in (None, "") for c in row):
            continue
        first_cell = _clean(row[0])
        narration = _clean(get(row, "البيان"))
        raw_date = get(row, "التاريخ")
        raw_balance = get(row, "الرصيد لكل حركة")

        if str(first_cell) in STOP_MARKERS:
            break

        is_header_row = str(first_cell) in ("0", "") and (raw_date in (0, "0", None, "") or "-" not in str(raw_date))
        if is_header_row:
            if narration and narration not in SKIP_MARKERS and re.match(r"^\d+-", narration):
                source_flag_mismatch = "غير مطابق" in str(raw_balance)
                m = re.match(r"^(\d+)-(.*)$", narration)
                code, name = (m.group(1), m.group(2)) if m else ("", narration)
                current = {
                    "code": code, "name": name.strip(), "rows": [],
                    "source_flagged_mismatch": source_flag_mismatch,
                }
                pharmacies.append(current)
            continue

        debit = _to_decimal(get(row, "مدين"))
        credit = _to_decimal(get(row, "دائن"))
        if debit == 0 and credit == 0:
            continue
        if current is None:
            continue
        current["rows"].append({
            "voucher_no": _clean(get(row, "رقم السند")),
            "narration": narration,
            "debit": debit,
            "credit": credit,
            "date": _clean(raw_date),
        })

    for ph in pharmacies:
        total_debit = sum((r["debit"] for r in ph["rows"]), Decimal("0"))
        total_credit = sum((r["credit"] for r in ph["rows"]), Decimal("0"))
        ph["total_debit"] = total_debit
        ph["total_credit"] = total_credit
        ph["difference"] = total_debit - total_credit
        ph["matched"] = abs(ph["difference"]) <= tolerance

    return pharmacies


def parse_hiba_statement(file_obj):
    """يقرأ ملف كشف حساب هبة (كشف إجمالي، غير مفصّل بالصيدلية) ويعيد إجمالياته،
    بالإضافة لقائمة كل حركاته منفردة (entries) — تُستخدم لاحقاً في مطابقة
    الحركات مع ملف مشروع دواك (انظر match_dawak_hiba_payments)."""
    wb = openpyxl.load_workbook(file_obj, data_only=True, read_only=True)
    ws = wb[wb.sheetnames[0]]
    rows = list(ws.iter_rows(values_only=True))
    wb.close()

    header_idx = header = None
    for i, row in enumerate(rows):
        cells = {str(_clean(c)) for c in row if c is not None}
        if {"مدين", "دائن", "البيان"}.issubset(cells):
            header_idx, header = i, [str(_clean(c)) for c in row]
            break
    if header_idx is None:
        raise ValueError("لم يتم العثور على صف العناوين المتوقع داخل ملف كشف حساب هبة.")

    col = {name: header.index(name) for name in header if name}
    total_debit = Decimal("0")
    total_credit = Decimal("0")
    count = 0
    entries = []
    order = 0
    for row in rows[header_idx + 1:]:
        if row is None or all(c in (None, "") for c in row):
            continue
        debit = _to_decimal(row[col["مدين"]]) if col.get("مدين") is not None and col["مدين"] < len(row) else Decimal("0")
        credit = _to_decimal(row[col["دائن"]]) if col.get("دائن") is not None and col["دائن"] < len(row) else Decimal("0")
        if debit == 0 and credit == 0:
            continue
        total_debit += debit
        total_credit += credit
        count += 1

        raw_date = row[col["التاريخ"]] if col.get("التاريخ") is not None and col["التاريخ"] < len(row) else None
        narration = row[col["البيان"]] if col.get("البيان") is not None and col["البيان"] < len(row) else None
        voucher_col = col.get("رقم القيد")
        voucher = row[voucher_col] if voucher_col is not None and voucher_col < len(row) else None
        cc_col = col.get("مركز الكلفة")
        cost_center = row[cc_col] if cc_col is not None and cc_col < len(row) else None
        account_col = col.get("الحساب")
        account = row[account_col] if account_col is not None and account_col < len(row) else None
        entries.append({
            "row_order": order,
            "voucher_no": _clean(voucher),
            "narration": _clean(narration),
            "debit": debit,
            "credit": credit,
            "raw_date": _clean(raw_date),
            "entry_date": _to_date(raw_date),
            "cost_center": _clean(cost_center),
            "account": _clean(account),
        })
        order += 1

    return {"total_debit": total_debit, "total_credit": total_credit,
            "balance": total_debit - total_credit, "rows_count": count, "entries": entries}


def _flatten_dawak_entries(pharmacies):
    """يحوّل حركات كل صيدليات ملف مشروع دواك إلى قائمة واحدة مسطّحة، كل عنصر
    يحمل مرجع الصيدلية (رمزها/اسمها) حتى يسهل تتبعه لاحقاً في نتائج المطابقة."""
    entries = []
    order = 0
    for ph in pharmacies:
        for r in ph["rows"]:
            entries.append({
                "row_order": order,
                "pharmacy_code": ph["code"],
                "pharmacy_name": ph["name"],
                "voucher_no": r["voucher_no"],
                "narration": r["narration"],
                "debit": r["debit"],
                "credit": r["credit"],
                "raw_date": r["date"],
                "entry_date": _to_date(r["date"]),
            })
            order += 1
    return entries


# --- مطابقة "مركز الكلفة" (ملف هبة) مع اسم الحساب الفرعي (ملف دواك) —
# راجع توثيق أعلى الملف لتفاصيل المشكلة والتحقق الفعلي. ---
def _cc_tokens(text):
    s = (text or "").replace("أ", "ا").replace("إ", "ا").replace("آ", "ا")
    s = s.replace("-", " ").replace("(", " ").replace(")", " ")
    s = re.sub(r"[.,]", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    tokens = set()
    for tok in s.split():
        if tok.startswith("ال") and len(tok) > 3:
            tok = tok[2:]
        if tok:
            tokens.add(tok)
    return tokens


def match_cost_center_to_pharmacy(cost_center_text, pharmacies, cutoff=0.6):
    """يبحث عن أفضل حساب فرعي بملف دواك (اسماً، مع رمزه) يطابق نص "مركز
    الكلفة" بملف هبة تقريبياً — تداخل الكلمات بعد التطبيع (لا تطابق حرفي،
    راجع توثيق أعلى الملف). يعيد (pharmacy, score) أو None إن لم يوجد أي
    تداخل يبلغ حد الثقة cutoff."""
    ctoks = _cc_tokens(cost_center_text)
    if not ctoks:
        return None
    best, best_score = None, 0.0
    for ph in pharmacies:
        ptoks = _cc_tokens(ph["name"])
        if not ptoks:
            continue
        inter = ctoks & ptoks
        if not inter:
            continue
        score = len(inter) / min(len(ctoks), len(ptoks))
        if score > best_score:
            best_score, best = score, ph
    if best is not None and best_score >= cutoff:
        return best, best_score
    return None


def resolve_cost_centers(pharmacies, hiba_entries, cutoff=0.6):
    """يُسنِد كل حركة هبة لها "مركز الكلفة" إلى الحساب الفرعي المطابق بملف
    دواك (يضيف hiba_pharmacy_code/hiba_pharmacy_name/cc_match_score لكل
    حركة مباشرة)، ويعيد أيضاً خريطة (نص مركز الكلفة الخام -> نتيجة
    المطابقة) للشفافية/التصحيح. لا يُسقِط أي حركة بصمت — الحركات التي
    تعذّرت مطابقتها تبقى بلا إسناد (hiba_pharmacy_code=None) لتُعرَض لاحقاً
    في شيت مستقل للمراجعة اليدوية."""
    cache = {}
    for e in hiba_entries:
        raw = e.get("cost_center") or ""
        if raw not in cache:
            cache[raw] = match_cost_center_to_pharmacy(raw, pharmacies, cutoff=cutoff) if raw else None
        found = cache[raw]
        if found:
            ph, score = found
            e["hiba_pharmacy_code"] = ph["code"]
            e["hiba_pharmacy_name"] = ph["name"]
            e["cc_match_score"] = score
        else:
            e["hiba_pharmacy_code"] = None
            e["hiba_pharmacy_name"] = None
            e["cc_match_score"] = None
    return cache


def compute_cost_center_reconciliation(pharmacies, hiba_entries, tolerance=Decimal("1")):
    """مطابقة تبادلية (راجع توثيق أعلى الملف) بين إجمالي كل حساب فرعي بملف
    دواك وإجمالي حركات هبة المُسنَدة إليه عبر مركز الكلفة: دائن دواك ضد
    مدين هبة، ومدين دواك ضد دائن هبة."""
    resolve_cost_centers(pharmacies, hiba_entries)

    by_pharmacy = defaultdict(list)
    unresolved = []
    for e in hiba_entries:
        if not e.get("cost_center"):
            continue
        if e.get("hiba_pharmacy_code"):
            by_pharmacy[e["hiba_pharmacy_code"]].append(e)
        else:
            unresolved.append(e)

    rows = []
    for ph in pharmacies:
        h_entries = by_pharmacy.get(ph["code"], [])
        hiba_debit = sum((e["debit"] for e in h_entries), Decimal("0"))
        hiba_credit = sum((e["credit"] for e in h_entries), Decimal("0"))
        has_hiba_data = len(h_entries) > 0
        diff_vs_hiba_debit = ph["total_credit"] - hiba_debit      # دائن دواك ضد مدين هبة
        diff_vs_hiba_credit = ph["total_debit"] - hiba_credit     # مدين دواك ضد دائن هبة
        if not has_hiba_data:
            status = "no_hiba_data"
        elif abs(diff_vs_hiba_debit) <= tolerance and abs(diff_vs_hiba_credit) <= tolerance:
            status = "matched"
        else:
            status = "mismatched"
        rows.append({
            "code": ph["code"], "name": ph["name"],
            "dawak_debit": ph["total_debit"], "dawak_credit": ph["total_credit"],
            "hiba_debit": hiba_debit, "hiba_credit": hiba_credit,
            "hiba_rows_count": len(h_entries),
            "diff_vs_hiba_debit": diff_vs_hiba_debit, "diff_vs_hiba_credit": diff_vs_hiba_credit,
            "status": status, "hiba_rows": h_entries,
        })

    summary = {
        "pharmacies_with_hiba_data": len([r for r in rows if r["status"] != "no_hiba_data"]),
        "matched": len([r for r in rows if r["status"] == "matched"]),
        "mismatched": len([r for r in rows if r["status"] == "mismatched"]),
        "no_hiba_data": len([r for r in rows if r["status"] == "no_hiba_data"]),
        "unresolved_hiba_rows": len(unresolved),
        "unresolved_hiba_amount": sum((e["debit"] + e["credit"] for e in unresolved), Decimal("0")),
    }
    return {"rows": rows, "unresolved": unresolved, "summary": summary}


def _secondary_lookup(entry, amount, other_entries, other_field):
    """فحص ثانوي: هل يوجد في *كامل* حركات الطرف الآخر (بلا استثناء ما استُخدم
    أصلاً في مقابلة أخرى) حركة بنفس المبلغ تماماً بأي تاريخ؟ عند وجود أكثر من
    مرشّح تُختار الأقرب بالتاريخ إلى الحركة الأصلية. يعيد (أقرب حركة, عدد كل
    المرشّحين) أو None إن لم يوجد المبلغ إطلاقاً."""
    candidates = [e for e in other_entries if e[other_field] == amount]
    if not candidates:
        return None
    if entry["entry_date"]:
        candidates = sorted(
            candidates,
            key=lambda e: abs((e["entry_date"] - entry["entry_date"]).days) if e["entry_date"] else 10 ** 6,
        )
    return candidates[0], len(candidates)


def match_dawak_hiba_payments(dawak_entries, hiba_entries):
    """يطابق حركات مشروع دواك (مسطّحة من كل الصيدليات) مع حركات كشف حساب هبة،
    بنفس أسلوب مطابقة هبة-سدانة (الفكرة الأولى):

        1) تُجمَّع الحركات حسب المبلغ الدقيق ضمن كل اتجاه (مدين دواك ⇄ دائن
           هبة، ودائن دواك ⇄ مدين هبة)، وتُقابَل بالتسلسل (نفس ترتيب ورودها
           في الملف الأصلي).
        2) أي حركة تبقى بلا مقابل ضمن مجموعة مبلغها تخضع لفحص ثانوي: نبحث في
           *كامل* حركات الطرف الآخر (حتى المُستخدمة أصلاً في مقابلة أخرى) عن
           نفس المبلغ بأي تاريخ. إن وُجدت لا تُصنَّف "فرق" مباشرة، بل تُصنَّف
           "موجود بتاريخ مختلف" مع عرض التاريخين معاً؛ فقط إن لم يوجد المبلغ
           إطلاقاً تُصنَّف "فرق حقيقي". لا نُخفي أي معلومة عن المستخدم بصمت.
    """
    dawak_groups_debit = defaultdict(list)
    dawak_groups_credit = defaultdict(list)
    for e in dawak_entries:
        if e["debit"] > 0:
            dawak_groups_debit[e["debit"]].append(e)
        if e["credit"] > 0:
            dawak_groups_credit[e["credit"]].append(e)

    hiba_groups_debit = defaultdict(list)
    hiba_groups_credit = defaultdict(list)
    for e in hiba_entries:
        if e["debit"] > 0:
            hiba_groups_debit[e["debit"]].append(e)
        if e["credit"] > 0:
            hiba_groups_credit[e["credit"]].append(e)

    def build_pair(a, b, amount, direction_label):
        day_diff = None
        status = "matched_same_day"
        note = ""
        if a["entry_date"] and b["entry_date"]:
            day_diff = abs((a["entry_date"] - b["entry_date"]).days)
            if day_diff > 0:
                status = "matched_date_diff"
                note = f"فرق بالتاريخ: {day_diff} يوم"
            if day_diff > 10:
                note += " — فرق كبير بالتاريخ، يُستحسن التحقق يدوياً"
        else:
            note = "تعذّر مقارنة التاريخ (تاريخ غير مقروء في أحد الملفين)"
        return {"a": a, "b": b, "amount": amount, "direction": direction_label,
                "status": status, "day_diff": day_diff, "note": note}

    def build_unmatched(entry, amount, other_entries, other_field, direction_label, side, other_label):
        found = _secondary_lookup(entry, amount, other_entries, other_field)
        if found:
            other, count = found
            extra = f" (ويوجد {count - 1} حركة إضافية بنفس المبلغ)" if count > 1 else ""
            entry_date_s = entry["entry_date"].isoformat() if entry["entry_date"] else (entry["raw_date"] or "غير معروف")
            other_date_s = other["entry_date"].isoformat() if other["entry_date"] else (other["raw_date"] or "غير معروف")
            day_diff = (abs((entry["entry_date"] - other["entry_date"]).days)
                        if entry["entry_date"] and other["entry_date"] else None)
            note = (f"موجود بنفس المبلغ ({amount}) عند {other_label} لكن بتاريخ مختلف: "
                    f"{entry_date_s} مقابل {other_date_s}.{extra} لم تُطابَق تلقائياً بسبب اختلاف "
                    "التاريخ/الترتيب — يُستحسن التحقق يدوياً (قد تكون استُهلكت أصلاً في مقابلة حركة أخرى).")
            a, b = (entry, other) if side == "dawak_only" else (other, entry)
            return {"a": a, "b": b, "amount": amount, "direction": direction_label,
                    "status": "found_diff_date", "day_diff": day_diff, "note": note}

        note = f"لا توجد أي حركة بنفس المبلغ ({amount}) عند {other_label} إطلاقاً — فرق حقيقي يستحق المراجعة."
        a, b = (entry, None) if side == "dawak_only" else (None, entry)
        return {"a": a, "b": b, "amount": amount, "direction": direction_label,
                "status": "true_diff", "day_diff": None, "note": note}

    def run_direction(a_groups, b_groups, direction_label, b_entries_full, a_entries_full, b_field, a_field):
        pairs = []
        for amount in set(a_groups) | set(b_groups):
            a_list = a_groups.get(amount, [])
            b_list = b_groups.get(amount, [])
            n = min(len(a_list), len(b_list))
            for i in range(n):
                pairs.append(build_pair(a_list[i], b_list[i], amount, direction_label))
            for a in a_list[n:]:
                pairs.append(build_unmatched(a, amount, b_entries_full, b_field, direction_label,
                                              "dawak_only", "هبة"))
            for b in b_list[n:]:
                pairs.append(build_unmatched(b, amount, a_entries_full, a_field, direction_label,
                                              "hiba_only", "دواك"))
        return pairs

    pairs = []
    pairs += run_direction(dawak_groups_debit, hiba_groups_credit, "dawak_debit_hiba_credit",
                            hiba_entries, dawak_entries, "credit", "debit")
    pairs += run_direction(dawak_groups_credit, hiba_groups_debit, "dawak_credit_hiba_debit",
                            hiba_entries, dawak_entries, "debit", "credit")

    matched = [p for p in pairs if p["status"] in ("matched_same_day", "matched_date_diff")]
    found_diff_date = [p for p in pairs if p["status"] == "found_diff_date"]
    true_diff = [p for p in pairs if p["status"] == "true_diff"]

    summary = {
        "dawak_entries_count": len(dawak_entries),
        "hiba_entries_count": len(hiba_entries),
        "matched_count": len(matched),
        "matched_same_day": len([p for p in matched if p["status"] == "matched_same_day"]),
        "matched_date_diff": len([p for p in matched if p["status"] == "matched_date_diff"]),
        "found_diff_date_count": len(found_diff_date),
        "found_diff_date_amount": sum((p["amount"] for p in found_diff_date), Decimal("0")),
        "true_diff_count": len(true_diff),
        "true_diff_amount": sum((p["amount"] for p in true_diff), Decimal("0")),
    }
    return {"pairs": pairs, "matched": matched, "found_diff_date": found_diff_date,
            "true_diff": true_diff, "summary": summary}


def build_result(pharmacies, hiba_totals):
    matched = [p for p in pharmacies if p["matched"]]
    mismatched = [p for p in pharmacies if not p["matched"]]
    summary = {
        "pharmacies_count": len(pharmacies),
        "matched_count": len(matched),
        "mismatched_count": len(mismatched),
        "mismatched_amount": sum((abs(p["difference"]) for p in mismatched), Decimal("0")),
        "dawak_total_debit": sum((p["total_debit"] for p in pharmacies), Decimal("0")),
        "dawak_total_credit": sum((p["total_credit"] for p in pharmacies), Decimal("0")),
        "hiba_total_debit": hiba_totals["total_debit"],
        "hiba_total_credit": hiba_totals["total_credit"],
        "hiba_balance": hiba_totals["balance"],
    }

    # مطابقة الحركات (دواك ⇄ هبة) — إضافة لاحقة، تُبنى فقط إن كان hiba_totals
    # يحمل قائمة حركات مفصّلة (entries)؛ محفوظة بشكل مستقل تماماً عن مطابقة
    # الصيدليات أعلاه حتى لا نغيّر سلوكها القائم.
    payments = None
    cost_centers = None
    if hiba_totals.get("entries") is not None:
        # تصحيح 2026-09-30: مطابقة مركز الكلفة أولاً (تُسنِد hiba_pharmacy_*
        # على كل حركة هبة مباشرة) — قبل تسطيح حركات دواك، حتى تستفيد مطابقة
        # الدفعات أدناه من هذا الإسناد أيضاً إن احتاجته لاحقاً.
        cost_centers = compute_cost_center_reconciliation(pharmacies, hiba_totals["entries"])
        dawak_entries = _flatten_dawak_entries(pharmacies)
        payments = match_dawak_hiba_payments(dawak_entries, hiba_totals["entries"])

    return {"pharmacies": pharmacies, "matched": matched, "mismatched": mismatched,
            "summary": summary, "payments": payments, "cost_centers": cost_centers}
