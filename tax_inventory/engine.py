"""
محرك مطابقة جرد الضريبة (أمين 8 مقابل أمين 9).

المنهجية المحدَّثة بطلب المستخدم صراحةً:

    ملف "الجرد فوق 3 قطع" (حقل الرفع over3_file) يمثّل بيانات "أمين 9":
    لكل مادة رقم إجمالي واحد فقط ("الكمية الحالية") بلا أي تفصيل صيدليات،
    وهو الرقم الأقل (السقف/الحد الأقصى) الذي يجب ألا نتجاوزه عند "البيع".

    ملف "حركة المبيعات" (حقل الرفع sales_file) يمثّل بيانات "أمين 8":
    التفصيل الحقيقي والكامل لكل مادة موزَّعاً على الصيدليات (عمود
    "اسم الزبون" = اسم الصيدلية في سياق هذا الملف)، وهو المرجع الصحيح
    للكمية الفعلية لكل صيدلية.

    لكل مادة: إن كان إجمالي أمين 8 (مجموع كل الصيدليات) أقل من أو يساوي
    سقف أمين 9، تُعتمد كل الصيدليات كاملة بلا استبعاد. أما إن كان الإجمالي
    أكبر من السقف، فيتم اختيار "أفضل مزيج" من الصيدليات (كل صيدلية بكامل
    كميتها، بلا تجزئة) بحيث يكون مجموعها أقرب ما يمكن لسقف أمين 9 دون
    تجاوزه (أقصى استخدام ممكن) — هذا هو الخيار الذي اختاره المستخدم صراحةً
    من بين ثلاثة بدائل (الأكبر أولاً / الأصغر أولاً / أفضل مزيج).

    ملف "الجرد تحت 3 قطع" (under3_file) يبقى فحصاً إعلامياً فقط كما كان:
    أي مادة من قائمة "فوق 3" تظهر أيضاً في قائمة "تحت 3" تُعلَّم بملاحظة
    توضيحية دون أي تأثير على التوزيع.
"""

from collections import defaultdict
from decimal import Decimal

import openpyxl

INVENTORY_SHEET = "المواد التي تجاوزت الحد"


def _clean(v):
    if v is None:
        return ""
    return str(v).strip() if isinstance(v, str) else v


def _to_number(v):
    if v is None or v == "":
        return 0
    if isinstance(v, (int, float, Decimal)):
        return v
    try:
        return float(str(v).replace(",", ""))
    except ValueError:
        return 0


def parse_inventory(file_obj):
    """يقرأ ملف جرد (فوق/تحت 3 قطع) ويعيد dict: اسم المادة -> (رمز المادة, الكمية)."""
    wb = openpyxl.load_workbook(file_obj, data_only=True, read_only=True)
    sheet_name = INVENTORY_SHEET if INVENTORY_SHEET in wb.sheetnames else wb.sheetnames[0]
    ws = wb[sheet_name]
    rows = list(ws.iter_rows(values_only=True))
    wb.close()

    if not rows:
        return {}
    header = [str(_clean(c)) for c in rows[0]]
    try:
        idx_code = header.index("رمز المادة")
        idx_name = header.index("اسم المادة")
        idx_qty = header.index("الكمية الحالية")
    except ValueError:
        idx_code, idx_name, idx_qty = 0, 1, 2

    items = {}
    for row in rows[1:]:
        if row is None or all(c in (None, "") for c in row):
            continue
        name = _clean(row[idx_name]) if idx_name < len(row) else None
        if not name:
            continue
        qty = _to_number(row[idx_qty]) if idx_qty < len(row) else 0
        code = _clean(row[idx_code]) if idx_code < len(row) else ""
        items[name] = {"code": code, "qty": qty}
    return items


SALES_HEADER_SIGNATURE = {"الفاتورة", "اسم المادة", "كمية"}
STOP_MARKERS = {"المجموع", "الرصيد النهائي"}


def parse_sales_quantities(file_obj):
    """يقرأ ملف حركة المبيعات ويعيد dict: اسم المادة -> إجمالي (كمية + هدايا)."""
    wb = openpyxl.load_workbook(file_obj, data_only=True, read_only=True)
    # نفضّل أي شيت اسمه فيه "نتيجة"، وإلا أول شيت فيه صف عناوين مطابق
    candidates = [n for n in wb.sheetnames if "نتيجة" in n] + list(wb.sheetnames)
    header_idx = header = ws = None
    for name in candidates:
        ws_try = wb[name]
        rows_try = list(ws_try.iter_rows(values_only=True))
        for i, row in enumerate(rows_try):
            cells = {str(_clean(c)) for c in row if c is not None}
            if SALES_HEADER_SIGNATURE.issubset(cells):
                ws, header_idx, header = ws_try, i, [str(_clean(c)) for c in row]
                all_rows = rows_try
                break
        if ws is not None:
            break
    if ws is None:
        wb.close()
        raise ValueError("لم يتم العثور على صف عناوين حركة المبيعات المتوقع (الفاتورة / اسم المادة / كمية).")

    col = {name: header.index(name) for name in header if name}
    totals = defaultdict(float)
    for row in all_rows[header_idx + 1:]:
        if row is None or all(c in (None, "") for c in row):
            continue
        first_cell = str(_clean(row[0])) if row[0] is not None else ""
        if first_cell in STOP_MARKERS:
            break
        name = row[col["اسم المادة"]] if col.get("اسم المادة") is not None and col["اسم المادة"] < len(row) else None
        name = _clean(name)
        if not name:
            continue
        qty = _to_number(row[col["كمية"]]) if col.get("كمية") is not None else 0
        gifts = _to_number(row[col["الهدايا"]]) if "الهدايا" in col and col["الهدايا"] < len(row) else 0
        totals[name] += qty + gifts
    wb.close()
    return dict(totals)


def parse_sales_detail_rows(file_obj):
    """يقرأ ملف حركة المبيعات ويعيد كل سطور الحركة بكامل حقولها (عدا الفاتورة
    والتاريخ، بحسب طلب المستخدم صراحةً)، مع عمود محسوب "اجمالي" = كمية + الهدايا
    (بنفس شكل شيت "تقرير نتيجة" المرجعي الموجود داخل ملف المبيعات نفسه)."""
    wb = openpyxl.load_workbook(file_obj, data_only=True, read_only=True)
    candidates = [n for n in wb.sheetnames if "نتيجة" in n] + list(wb.sheetnames)
    header_idx = header = ws = all_rows = None
    for name in candidates:
        ws_try = wb[name]
        rows_try = list(ws_try.iter_rows(values_only=True))
        for i, row in enumerate(rows_try):
            cells = {str(_clean(c)) for c in row if c is not None}
            if SALES_HEADER_SIGNATURE.issubset(cells):
                ws, header_idx, header = ws_try, i, [str(_clean(c)) for c in row]
                all_rows = rows_try
                break
        if ws is not None:
            break
    if ws is None:
        wb.close()
        raise ValueError("لم يتم العثور على صف عناوين حركة المبيعات المتوقع (الفاتورة / اسم المادة / كمية).")

    col = {name: header.index(name) for name in header if name}

    def get(row, name):
        idx = col.get(name)
        if idx is None or idx >= len(row):
            return None
        return row[idx]

    rows = []
    for row in all_rows[header_idx + 1:]:
        if row is None or all(c in (None, "") for c in row):
            continue
        first_cell = str(_clean(row[0])) if row[0] is not None else ""
        if first_cell in STOP_MARKERS:
            break
        name = _clean(get(row, "اسم المادة"))
        if not name:
            continue
        qty = _to_number(get(row, "كمية"))
        gifts = _to_number(get(row, "الهدايا"))
        rows.append({
            "customer": _clean(get(row, "اسم الزبون")),
            "name": name,
            "group": _clean(get(row, "المجموعة")),
            "qty": qty,
            "gifts": gifts,
            "total_qty": qty + gifts,
            "unit_price": _to_number(get(row, "الإفرادي")),
            "total_price": _to_number(get(row, "السعر الإجمالي")),
        })
    wb.close()
    return rows


UNKNOWN_PHARMACY = "(بدون اسم زبون/صيدلية)"

# حد أمان لأداء خوارزمية أفضل مزيج (subset-sum): إن تجاوز عدد الصيدليات ×
# السقف هذا الحد، نتحول لتقريب أسرع (الأكبر أولاً) بدل التعليق، مع تعليم
# ذلك بوضوح في الملاحظة (لا تخمين صامت).
_DP_SAFETY_LIMIT = 3_000_000


def build_pharmacy_breakdown(sales_detail_rows):
    """يبني dict: اسم المادة -> dict: اسم الصيدلية (اسم الزبون) -> إجمالي
    الكمية (كمية + هدايا)، من تفصيل حركة المبيعات (أمين 8).

    ملاحظة: هذا الإجمالي (total_qty = كمية + هدايا) هو ما يُستخدم في خوارزمية
    التوزيع (السقف/أفضل مزيج) — انظر `build_pharmacy_gifts_breakdown` للحصول
    على مجموع الهدايا وحدها لكل مادة/صيدلية (إعلامي فقط، لا يؤثر على القرار)."""
    breakdown = defaultdict(lambda: defaultdict(float))
    for r in sales_detail_rows:
        pharmacy = r.get("customer") or UNKNOWN_PHARMACY
        breakdown[r["name"]][pharmacy] += r.get("total_qty", 0)
    return breakdown


def build_pharmacy_gifts_breakdown(sales_detail_rows):
    """يبني dict: اسم المادة -> dict: اسم الصيدلية (اسم الزبون) -> إجمالي
    الهدايا فقط، من تفصيل حركة المبيعات (أمين 8). إعلامي فقط (لا يدخل في
    منطق التوزيع/السقف)."""
    gifts_breakdown = defaultdict(lambda: defaultdict(float))
    for r in sales_detail_rows:
        pharmacy = r.get("customer") or UNKNOWN_PHARMACY
        gifts_breakdown[r["name"]][pharmacy] += r.get("gifts", 0)
    return gifts_breakdown


def _select_best_combination(pharmacy_qtys, cap):
    """يختار مجموعة الصيدليات (كل واحدة بكامل كميتها) التي يكون مجموعها
    أقرب ما يمكن لسقف `cap` دون تجاوزه (أقصى استخدام ممكن / أفضل مزيج).

    pharmacy_qtys: قائمة [(اسم الصيدلية, الكمية), ...]
    يعيد: (مجموعة أسماء الصيدليات المختارة, المجموع المحقَّق, approx: bool)
    """
    cap_i = int(round(cap))
    items = [(name, int(round(qty))) for name, qty in pharmacy_qtys if qty]
    if cap_i <= 0 or not items:
        return set(), 0, False

    n = len(items)
    if n * max(cap_i, 1) > _DP_SAFETY_LIMIT:
        # تقريب (الأكبر أولاً) فقط لحالات ضخمة جداً يتعذّر فيها الحل الأمثل
        # بوقت معقول — يُعلَّم صراحة في note بحقل approx.
        selected, total = set(), 0
        for name, qty in sorted(items, key=lambda x: -x[1]):
            if total + qty <= cap_i:
                selected.add(name)
                total += qty
        return selected, total, True

    dp = [False] * (cap_i + 1)
    dp[0] = True
    take = [[False] * (cap_i + 1) for _ in range(n)]
    for i, (_, qty) in enumerate(items):
        if qty <= 0 or qty > cap_i:
            continue
        for s in range(cap_i, qty - 1, -1):
            if not dp[s] and dp[s - qty]:
                dp[s] = True
                take[i][s] = True

    best = 0
    for s in range(cap_i, -1, -1):
        if dp[s]:
            best = s
            break

    selected = set()
    s = best
    for i in range(n - 1, -1, -1):
        if take[i][s]:
            selected.add(items[i][0])
            s -= items[i][1]
    return selected, best, False


def build_detail_rows(sales_detail_rows, over3_items):
    """يبني "نموذج جرد الضريبة" التفصيلي: كل سطور حركة المبيعات لمادة موجودة
    ضمن قائمة (فوق 3 قطع)، بكامل الحقول الأصلية عدا الفاتورة والتاريخ (بحسب
    طلب المستخدم صراحةً)، مرتبة حسب اسم المادة ثم اسم الزبون."""
    rows = [r for r in sales_detail_rows if r["name"] in over3_items]
    rows.sort(key=lambda r: (r["name"], r["customer"]))
    return rows


def reconcile(over3_items, under3_items, sales_detail_rows):
    """يقارن سقف أمين 9 (over3_items) بتفصيل أمين 8 الحقيقي على مستوى
    الصيدلية (sales_detail_rows)، ويوزّع/يختار أفضل مزيج من الصيدليات
    (كل واحدة بكامل كميتها) بحيث لا يتجاوز المجموع سقف أمين 9، مع أقصى
    استخدام ممكن — بالطريقة التي اختارها المستخدم صراحة."""
    breakdown = build_pharmacy_breakdown(sales_detail_rows)
    gifts_breakdown = build_pharmacy_gifts_breakdown(sales_detail_rows)
    rows = []
    pharmacy_rows = []
    approx_count = 0

    for name, info in over3_items.items():
        cap = info["qty"]
        pharmacies = breakdown.get(name, {})
        pharmacy_list = sorted(pharmacies.items(), key=lambda kv: -kv[1])
        true_total = sum(qty for _, qty in pharmacy_list)

        notes = []
        if name in under3_items:
            notes.append("تنبيه: هذه المادة ظهرت أيضاً ضمن قائمة (تحت 3 قطع).")

        if not pharmacy_list:
            selected_names, allocated, approx = set(), 0, False
            if cap:
                notes.append("لا توجد مبيعات مطابقة لهذه المادة في ملف أمين 8 (أمين 9).")
        elif true_total <= cap:
            # الكمية الحقيقية كاملة (أمين 8) لا تتجاوز سقف أمين 9 — تُعتمد
            # كل الصيدليات كاملة بلا أي استبعاد.
            selected_names = {p for p, _ in pharmacy_list}
            allocated = true_total
            approx = False
        else:
            selected_names, allocated, approx = _select_best_combination(pharmacy_list, cap)
            excluded = [p for p, _ in pharmacy_list if p not in selected_names]
            if excluded:
                notes.append(
                    "تم تجاوز سقف أمين 9 (%s) فاعتُمد أفضل مزيج من الصيدليات (استخدام %s من %s)؛ "
                    "الصيدليات المستبعدة من هذا التوزيع: %s."
                    % (cap, allocated, true_total, "، ".join(excluded))
                )
            if approx:
                approx_count += 1
                notes.append("تنبيه: عدد الصيدليات/السقف كبير جداً، استُخدم تقريب (الأكبر أولاً) بدل الحل الأمثل الكامل.")

        note = " ".join(notes)
        is_capped = bool(pharmacy_list) and true_total > cap

        rows.append({
            "code": info["code"],
            "name": name,
            "inventory_qty": cap,          # سقف أمين 9
            "sold_qty": true_total,        # إجمالي أمين 8 الحقيقي الكامل
            "final_qty": allocated,        # الكمية المسموح "بيعها" فعلياً بعد التوزيع
            "is_capped": is_capped,
            "pharmacy_count": len(pharmacy_list),
            "selected_pharmacy_count": len(selected_names),
            "note": note,
        })

        material_gifts = gifts_breakdown.get(name, {})
        for pharmacy, qty in pharmacy_list:
            pharmacy_rows.append({
                "material": name,
                "code": info["code"],
                "pharmacy": pharmacy,
                "qty": qty,
                "gifts": material_gifts.get(pharmacy, 0),
                "selected": pharmacy in selected_names,
                "allocated_qty": qty if pharmacy in selected_names else 0,
            })

    rows.sort(key=lambda r: r["name"])
    pharmacy_rows.sort(key=lambda r: (r["material"], -r["qty"]))

    summary = {
        "items_over3": len(over3_items),
        "items_matched_in_sales": len([r for r in rows if r["sold_qty"] > 0]),
        "total_inventory_qty": sum(r["inventory_qty"] for r in rows),
        "total_sold_qty": sum(r["sold_qty"] for r in rows),
        "total_final_qty": sum(r["final_qty"] for r in rows),
        "cross_listed_count": len([r for r in rows if "تحت 3 قطع" in r["note"]]),
        "capped_items_count": len([r for r in rows if r["is_capped"]]),
        "approx_items_count": approx_count,
    }
    return {"rows": rows, "summary": summary, "pharmacy_rows": pharmacy_rows}
