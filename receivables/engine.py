"""محرك مطابقة الذمم مع قسم التوزيع (الفكرة الخامسة).

كل حركة في دفتر الأستاذ يُشار في نص "البيان" الخاص بها إلى رقم/أرقام
"كشف" (رقم البيان) المرتبطة بها، مثال:
    "... ايصال 38131  كشف 3056-3058-3057  يومية 16-8-2026"   → الأرقام 3056, 3057, 3058
    "... كشف رقم 3077 يومية 16.8.2026"                        → الرقم 3077

المطابقة المطلوبة: تجميع كل الدفعات الدائنة المرتبطة بنفس رقم البيان
ومقارنتها بالرصيد المدين لنفس الرقم. بما أن حركة واحدة قد تغطي عدة أرقام
بيان دفعة واحدة (كما في المثال أعلاه)، لا يمكن فصل مبلغها على كل رقم على
حدة بدقة — لذلك تُجمَّع كل الحركات التي تشترك في أي رقم بيان واحد ضمن
"مجموعة مطابقة" واحدة (خوارزمية Union-Find)، وتتم المقارنة على مستوى
المجموعة كاملة، مع عرض كل أرقام البيان التي تضمّها.
"""

import re
from decimal import Decimal

import openpyxl

STATEMENT_PATTERN = re.compile(r"كشف\s*(?:رقم)?\s*[:\-]?\s*([\d][\d\-،,\s]*\d|\d)")
NUMBER_SPLIT = re.compile(r"[^\d]+")

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


def extract_statement_numbers(narration):
    numbers = set()
    for match in STATEMENT_PATTERN.finditer(narration or ""):
        chunk = match.group(1)
        for part in NUMBER_SPLIT.split(chunk):
            if part and part.isdigit():
                numbers.add(part)
    return numbers


def parse_ledger(file_obj):
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
        raise ValueError("لم يتم العثور على صف العناوين المتوقع داخل الملف.")

    col = {name: header.index(name) for name in header if name}

    def get(row, name):
        idx = col.get(name)
        if idx is None or idx >= len(row):
            return None
        return row[idx]

    current_subaccount = ""
    rows = []
    for row in all_rows[header_idx + 1:]:
        if row is None or all(c in (None, "") for c in row):
            continue
        first_cell = _clean(row[0])
        narration = _clean(get(row, "البيان"))
        if str(first_cell) in STOP_MARKERS:
            break

        debit = _to_decimal(get(row, "مدين"))
        credit = _to_decimal(get(row, "دائن"))
        raw_date = get(row, "التاريخ")

        # صفوف عناوين/إجماليات الحسابات الفرعية: رقم السند = 0 والتاريخ = 0 (ليست حركة مؤرَّخة فعلية)
        is_header_or_total_row = (
            str(first_cell) in ("0", "")
            and (raw_date in (0, "0", None, "") or "-" not in str(raw_date))
        )
        if is_header_or_total_row:
            if narration and narration not in SKIP_MARKERS and re.match(r"^\d+-", narration):
                current_subaccount = narration
            continue
        if debit == 0 and credit == 0:
            continue

        rows.append({
            "voucher_no": _clean(get(row, "رقم السند")),
            "narration": narration,
            "debit": debit,
            "credit": credit,
            "date": _clean(get(row, "التاريخ")),
            "subaccount": current_subaccount,
            "statement_numbers": extract_statement_numbers(narration),
        })
    return rows


def _union_find_groups(rows):
    parent = list(range(len(rows)))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    number_to_row = {}
    for i, r in enumerate(rows):
        for num in r["statement_numbers"]:
            if num in number_to_row:
                union(i, number_to_row[num])
            else:
                number_to_row[num] = i

    groups = {}
    for i in range(len(rows)):
        root = find(i)
        groups.setdefault(root, []).append(i)
    return groups


def reconcile(rows, tolerance=Decimal("1")):
    linked = [r for r in rows if r["statement_numbers"]]
    unlinked = [r for r in rows if not r["statement_numbers"]]

    groups = _union_find_groups(linked)

    results = []
    for indices in groups.values():
        group_rows = [linked[i] for i in indices]
        all_numbers = sorted({n for r in group_rows for n in r["statement_numbers"]}, key=int)
        total_debit = sum((r["debit"] for r in group_rows), Decimal("0"))
        total_credit = sum((r["credit"] for r in group_rows), Decimal("0"))
        diff = total_credit - total_debit
        matched = abs(diff) <= tolerance
        results.append({
            "statement_numbers": all_numbers,
            "rows": group_rows,
            "total_debit": total_debit,
            "total_credit": total_credit,
            "difference": diff,
            "matched": matched,
            "subaccounts": sorted({r["subaccount"] for r in group_rows if r["subaccount"]}),
        })

    results.sort(key=lambda g: (int(g["statement_numbers"][0]) if g["statement_numbers"] else 0))
    matched_groups = [g for g in results if g["matched"]]
    mismatched_groups = [g for g in results if not g["matched"]]

    summary = {
        "total_rows": len(rows),
        "linked_rows": len(linked),
        "unlinked_rows": len(unlinked),
        "groups_count": len(results),
        "matched_groups": len(matched_groups),
        "mismatched_groups": len(mismatched_groups),
        "mismatched_amount": sum((abs(g["difference"]) for g in mismatched_groups), Decimal("0")),
    }
    return {
        "groups": results,
        "matched_groups": matched_groups,
        "mismatched_groups": mismatched_groups,
        "unlinked": unlinked,
        "summary": summary,
    }
