"""
محرك مطابقة كشفي حساب هبة وسدانة (الفكرة الأولى).

المنطق:
    كل طرف (هبة / سدانة) يمسك "دفتر أستاذ" لنفس العلاقة المالية بينهما،
    وأي دفعة تُسجَّل في أحد الطرفين كـ "مدين" تُسجَّل في الطرف الآخر
    كـ "دائن" بنفس المبلغ تقريباً (وأحياناً بفارق يوم أو أكثر بسبب توقيت
    الترحيل). لذلك تتم المطابقة عبر:

        1) تجميع حركات "مدين" عند هبة مع حركات "دائن" عند سدانة، كل مجموعة
           حسب المبلغ الدقيق.
        2) تجميع حركات "دائن" عند هبة مع حركات "مدين" عند سدانة، بنفس الطريقة.
        3) داخل كل مجموعة مبلغ، تُقابَل الحركات بالتسلسل (نفس ترتيب ورودها
           في ملف الإكسل الأصلي) بين الطرفين. هذا يطابق طلب المستخدم بأن
           تكون المقابلة "بنفس ترتيب ملف الإكسل".
        4) أي حركة تبقى بدون مقابل ضمن مجموعة مبلغها (أي لم يعد هناك عدد
           كافٍ من حركات الطرف الآخر بنفس المبلغ لمقابلتها) تخضع لفحص
           ثانوي: نبحث في **كامل** حركات الطرف الآخر (وليس فقط الفائض غير
           المستخدم منها — حتى لو كانت تلك الحركة استُهلكت أصلاً في مقابلة
           غيرها بسبب الترتيب/التسلسل) عن حركة بنفس المبلغ تماماً وبأي
           تاريخ. إن وُجدت، لا تُصنَّف "فرق" مباشرة، بل تُصنَّف تصنيفاً
           مستقلاً "موجود بنفس المبلغ بتاريخ مختلف" مع عرض التاريخين معاً؛
           فقط إن لم يوجد أي مبلغ مطابق إطلاقاً في الطرف الآخر تُصنَّف
           "فرق حقيقي". الهدف عدم إخفاء أي معلومة عن المستخدم (فلسفة
           المشروع: لا نُسقط صفاً بصمت، بل نُنبّه عليه بوضوح).

هذا المنطق كامل بالبايثون/الحسابات الحتمية، لا يعتمد على أي ذكاء اصطناعي،
بحيث تكون النتيجة قابلة للتفسير والتدقيق بشكل كامل.
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal, InvalidOperation

import openpyxl

HEADER_SIGNATURE = {"رقم السند", "مدين", "دائن", "التاريخ"}
STOP_MARKERS = {"المجموع", "الرصيد النهائي"}
SKIP_MARKERS = {"الرصيد السابق"}


def _clean(v):
    if v is None:
        return ""
    if isinstance(v, str):
        return v.strip()
    return v


def _to_decimal(v) -> Decimal:
    v = _clean(v)
    if v == "" or v is None:
        return Decimal("0")
    if isinstance(v, (int, float, Decimal)):
        try:
            return Decimal(str(v)).quantize(Decimal("0.01"))
        except InvalidOperation:
            return Decimal("0")
    s = str(v).replace(",", "").strip()
    if s in ("", "-"):
        return Decimal("0")
    try:
        return Decimal(s).quantize(Decimal("0.01"))
    except InvalidOperation:
        return Decimal("0")


def _to_date(v):
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


@dataclass
class LedgerEntry:
    side: str  # "hiba" or "sadana"
    row_order: int
    voucher_no: str
    narration: str
    debit: Decimal
    credit: Decimal
    entry_date: date | None
    raw_date: str
    contra_account: str
    matched: bool = False


@dataclass
class MatchPair:
    a: LedgerEntry | None
    b: LedgerEntry | None
    amount: Decimal
    direction: str  # "hiba_debit_sadana_credit" or "hiba_credit_sadana_debit"
    # status: "matched_same_day" | "matched_date_diff" |
    #         "hiba_only_found_diff_date" | "sadana_only_found_diff_date" (فحص ثانوي: نفس المبلغ موجود
    #         عند الطرف الآخر لكن بتاريخ مختلف - وربما استُهلك أصلاً بمقابلة أخرى) |
    #         "hiba_only" | "sadana_only" (فرق حقيقي: لا يوجد هذا المبلغ إطلاقاً عند الطرف الآخر)
    status: str
    day_diff: int | None
    note: str = ""
    other_date_note: str = ""  # عند "found_diff_date": التاريخ الأصلي مقابل تاريخ الحركة الموجودة بمبلغ مطابق


class LedgerParseError(Exception):
    pass


def find_header_row(rows):
    for i, row in enumerate(rows):
        cells = {str(_clean(c)) for c in row if c is not None}
        if HEADER_SIGNATURE.issubset(cells):
            return i, row
    raise LedgerParseError(
        "لم يتم العثور على صف العناوين المتوقع (رقم السند / مدين / دائن / التاريخ) داخل الملف."
    )


def parse_ledger(file_obj, side, sheet_name=None):
    """يقرأ ملف إكسل بصيغة (دفتر الأستاذ) ويحوّله لقائمة LedgerEntry."""
    wb = openpyxl.load_workbook(file_obj, data_only=True, read_only=True)
    ws = wb[sheet_name] if sheet_name else wb[wb.sheetnames[0]]
    all_rows = list(ws.iter_rows(values_only=True))
    wb.close()

    header_idx, header_row = find_header_row(all_rows)
    header = [str(_clean(c)) for c in header_row]
    col = {name: header.index(name) for name in header if name}

    def get(row, name, default=None):
        idx = col.get(name)
        if idx is None or idx >= len(row):
            return default
        return row[idx]

    entries = []
    order = 0
    for row in all_rows[header_idx + 1:]:
        if row is None or all(c in (None, "") for c in row):
            continue
        first_cell = str(_clean(row[0])) if row[0] is not None else ""
        if first_cell in STOP_MARKERS:
            break
        if first_cell in SKIP_MARKERS:
            continue

        debit = _to_decimal(get(row, "مدين"))
        credit = _to_decimal(get(row, "دائن"))
        if debit == 0 and credit == 0:
            continue

        raw_date = get(row, "التاريخ")
        entry_date = _to_date(raw_date)

        entries.append(
            LedgerEntry(
                side=side,
                row_order=order,
                voucher_no=str(_clean(get(row, "رقم السند", ""))),
                narration=str(_clean(get(row, "البيان", ""))),
                debit=debit,
                credit=credit,
                entry_date=entry_date,
                raw_date=str(_clean(raw_date)),
                contra_account=str(_clean(get(row, "الحساب المقابل", ""))),
            )
        )
        order += 1

    return entries


def _match_direction(hiba_entries, sadana_entries, hiba_field, sadana_field, direction_label,
                      hiba_period, sadana_period):
    """يطابق حركات هبة (حقل hiba_field) مع حركات سدانة (حقل sadana_field) بنفس المبلغ، بالتسلسل."""
    from collections import defaultdict

    hiba_groups = defaultdict(list)
    for e in hiba_entries:
        amt = getattr(e, hiba_field)
        if amt > 0:
            hiba_groups[amt].append(e)

    sadana_groups = defaultdict(list)
    for e in sadana_entries:
        amt = getattr(e, sadana_field)
        if amt > 0:
            sadana_groups[amt].append(e)

    pairs = []
    all_amounts = set(hiba_groups) | set(sadana_groups)
    for amount in all_amounts:
        h_list = hiba_groups.get(amount, [])
        s_list = sadana_groups.get(amount, [])
        n = min(len(h_list), len(s_list))
        for i in range(n):
            h, s = h_list[i], s_list[i]
            h.matched = True
            s.matched = True
            day_diff = None
            status = "matched_same_day"
            note = ""
            if h.entry_date and s.entry_date:
                day_diff = abs((h.entry_date - s.entry_date).days)
                if day_diff > 0:
                    status = "matched_date_diff"
                    note = f"فرق بالتاريخ: {day_diff} يوم"
                if day_diff > 10:
                    note += " — فرق كبير بالتاريخ، يُستحسن التحقق يدوياً"
            else:
                note = "تعذّر مقارنة التاريخ (تاريخ غير مقروء في أحد الملفين)"
            pairs.append(MatchPair(a=h, b=s, amount=amount, direction=direction_label,
                                    status=status, day_diff=day_diff, note=note))
        # الفائض من جهة هبة بلا مقابل ضمن هذه المجموعة: نبحث ثانوياً في *كامل* حركات
        # سدانة (حقل sadana_field) عن نفس المبلغ بأي تاريخ قبل اعتبارها فرقاً حقيقياً
        for h in h_list[n:]:
            pairs.append(_unmatched_pair(h, sadana_entries, sadana_field, amount,
                                          direction_label, sadana_period, "hiba_only"))
        # الفائض من جهة سدانة بلا مقابل ضمن هذه المجموعة: نفس الفحص الثانوي في حركات هبة
        for s in s_list[n:]:
            pairs.append(_unmatched_pair(s, hiba_entries, hiba_field, amount,
                                          direction_label, hiba_period, "sadana_only"))

    return pairs


def _unmatched_pair(entry, other_entries, other_field, amount, direction_label, period, which):
    """يُبنى لأي حركة بقيت بلا مقابل ضمن مجموعة مبلغها. قبل تصنيفها "فرق حقيقي"،
    نبحث ثانوياً في كامل حركات الطرف الآخر (حتى المُستخدمة أصلاً في مقابلة أخرى)
    عن نفس المبلغ تماماً بأي تاريخ — إن وُجدت نصنّفها "موجود بتاريخ مختلف" بدل
    "فرق"، ونعرض كلا التاريخين، حسب طلب المستخدم وفلسفة عدم إخفاء أي معلومة."""
    candidates = [e for e in other_entries if getattr(e, other_field) == amount]
    if candidates:
        if entry.entry_date:
            candidates = sorted(
                candidates,
                key=lambda e: abs((e.entry_date - entry.entry_date).days) if e.entry_date else 10 ** 6,
            )
        closest = candidates[0]
        extra = f" (ويوجد {len(candidates) - 1} حركة إضافية بنفس المبلغ في الطرف الآخر)" if len(candidates) > 1 else ""
        entry_date_s = entry.entry_date.isoformat() if entry.entry_date else (entry.raw_date or "غير معروف")
        closest_date_s = closest.entry_date.isoformat() if closest.entry_date else (closest.raw_date or "غير معروف")
        day_diff = (abs((entry.entry_date - closest.entry_date).days)
                    if entry.entry_date and closest.entry_date else None)
        note = (f"موجود بنفس المبلغ ({amount}) في الطرف الآخر لكن بتاريخ مختلف: "
                f"{entry_date_s} مقابل {closest_date_s}.{extra} لم تُطابَق تلقائياً بسبب اختلاف "
                "التاريخ — يُستحسن التحقق يدوياً (قد تكون استُهلكت أصلاً في مقابلة حركة أخرى بنفس المبلغ).")
        status = f"{which}_found_diff_date"
        h = entry if which == "hiba_only" else closest
        s = closest if which == "hiba_only" else entry
        return MatchPair(a=h, b=s, amount=amount, direction=direction_label,
                          status=status, day_diff=day_diff, note=note)

    note = "لا يوجد أي قيد بنفس المبلغ في الطرف الآخر إطلاقاً — فرق حقيقي يستحق المراجعة."
    if entry.entry_date and period:
        other_min, other_max = period
        if other_min and other_max and not (other_min <= entry.entry_date <= other_max):
            note = "خارج الفترة الزمنية المتوفرة في الطرف الآخر — قد لا يكون خطأً فعلياً."
    h = entry if which == "hiba_only" else None
    s = entry if which == "sadana_only" else None
    return MatchPair(a=h, b=s, amount=amount, direction=direction_label,
                      status=which, day_diff=None, note=note)


def reconcile(hiba_entries, sadana_entries):
    hiba_dates = [e.entry_date for e in hiba_entries if e.entry_date]
    sadana_dates = [e.entry_date for e in sadana_entries if e.entry_date]
    hiba_period = (min(hiba_dates), max(hiba_dates)) if hiba_dates else (None, None)
    sadana_period = (min(sadana_dates), max(sadana_dates)) if sadana_dates else (None, None)

    pairs = []
    # مدين عند هبة  <->  دائن عند سدانة
    pairs += _match_direction(
        hiba_entries, sadana_entries, "debit", "credit",
        "hiba_debit_sadana_credit", hiba_period, sadana_period,
    )
    # دائن عند هبة  <->  مدين عند سدانة
    pairs += _match_direction(
        hiba_entries, sadana_entries, "credit", "debit",
        "hiba_credit_sadana_debit", hiba_period, sadana_period,
    )

    matched = [p for p in pairs if p.status in ("matched_same_day", "matched_date_diff")]
    # فرق حقيقي: لا يوجد نفس المبلغ إطلاقاً عند الطرف الآخر
    hiba_only = [p for p in pairs if p.status == "hiba_only"]
    sadana_only = [p for p in pairs if p.status == "sadana_only"]
    # موجود بنفس المبلغ لكن بتاريخ مختلف (فحص ثانوي) — لا تُحسب "فرق"، فئة مستقلة
    hiba_found_diff_date = [p for p in pairs if p.status == "hiba_only_found_diff_date"]
    sadana_found_diff_date = [p for p in pairs if p.status == "sadana_only_found_diff_date"]
    found_diff_date = hiba_found_diff_date + sadana_found_diff_date

    summary = {
        "hiba_count": len(hiba_entries),
        "sadana_count": len(sadana_entries),
        "matched_count": len(matched),
        "matched_same_day": len([p for p in matched if p.status == "matched_same_day"]),
        "matched_date_diff": len([p for p in matched if p.status == "matched_date_diff"]),
        "found_diff_date_count": len(found_diff_date),
        "found_diff_date_amount": sum((p.amount for p in found_diff_date), Decimal("0")),
        "hiba_only_count": len(hiba_only),
        "sadana_only_count": len(sadana_only),
        "hiba_only_amount": sum((p.amount for p in hiba_only), Decimal("0")),
        "sadana_only_amount": sum((p.amount for p in sadana_only), Decimal("0")),
        "hiba_period": hiba_period,
        "sadana_period": sadana_period,
        "has_errors": bool(hiba_only or sadana_only),
    }
    return {
        "matched": matched,
        "found_diff_date": found_diff_date,
        "hiba_only": hiba_only,
        "sadana_only": sadana_only,
        "all_pairs": pairs,
        "summary": summary,
    }
