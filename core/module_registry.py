"""
سجل الحلول (الوحدات) التسعة داخل النظام.

هذا السجل هو مصدر الحقيقة الوحيد لأسماء الوحدات وروابطها وأيقوناتها،
وتُستخدم "الأكواد" (code) هنا لضبط صلاحيات كل مستخدم على كل وحدة
عبر نموذج ModuleAccess، بدل ترميز الصلاحيات يدوياً في كل تطبيق.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ModuleDef:
    code: str
    name: str
    short_name: str
    description: str
    icon: str  # اسم أيقونة Bootstrap Icons
    url_name: str  # اسم رابط index الخاص بالتطبيق
    color: str  # لون مميز للوحدة في الواجهة


MODULES = [
    ModuleDef(
        code="reconciliation_hs",
        name="مطابقة هبة - سدانة",
        short_name="مطابقة هبة/سدانة",
        description="مطابقة كشفي حساب هبة وسدانة آلياً حسب المبلغ والتاريخ، وإظهار الفروقات والأخطاء.",
        icon="bi-arrow-left-right",
        url_name="reconciliation_hs:index",
        color="#2563eb",
    ),
    ModuleDef(
        code="commissions",
        name="عمولات المندوبين",
        short_name="عمولات المندوبين",
        description="احتساب عمولة كل مندوب/كول سنتر حسب الشركة من حركة المبيعات والمرتجعات، وعمولة المعقمات والتارغت.",
        icon="bi-percent",
        url_name="commissions:index",
        color="#0d9488",
    ),
    ModuleDef(
        code="distributor_commissions",
        name="عمولة تحصيل الموزعين الداخليين",
        short_name="عمولة الموزعين",
        description="احتساب عمولة تحصيل الموزعين الداخليين (سائق/مساعد/دراجة) من دفتر أستاذ ذمم قسم التوزيع. وحدة وصلاحية مستقلة عن عمولات المندوبين.",
        icon="bi-bicycle",
        url_name="distributor_commissions:index",
        color="#65a30d",
    ),
    ModuleDef(
        code="data_cleaning",
        name="تنظيف داتا",
        short_name="تنظيف داتا",
        description="تحويل ملفات المبيعات والمرتجعات والذمم إلى تنسيق موحّد ونظيف جاهز للاستخدام.",
        icon="bi-funnel",
        url_name="data_cleaning:index",
        color="#7c3aed",
    ),
    ModuleDef(
        code="tax_inventory",
        name="مطابقة جرد الضريبة",
        short_name="جرد الضريبة",
        description="مقارنة جرد المواد فوق 3 قطع مع حركة المبيعات لاستخراج الفائض الصحيح كعدد صحيح غير سالب.",
        icon="bi-clipboard-check",
        url_name="tax_inventory:index",
        color="#ca8a04",
    ),
    ModuleDef(
        code="receivables",
        name="مطابقة الذمم مع قسم التوزيع",
        short_name="مطابقة الذمم",
        description="مطابقة أرصدة المدين والدائن حسب رقم البيان، مع تجميع الدفعات المتعددة لنفس البيان.",
        icon="bi-diagram-3",
        url_name="receivables:index",
        color="#db2777",
    ),
    ModuleDef(
        code="dawak_compare",
        name="مطابقة دواك",
        short_name="مطابقة دواك",
        description="مقارنة كشف حساب هبة مع مشروع دواك بعد خصم الحسومات، وتحديد أي صيدلية فيها فرق.",
        icon="bi-shop",
        url_name="dawak_compare:index",
        color="#059669",
    ),
    ModuleDef(
        code="account_statement",
        name="فصل كشف الحساب (ليرة/دولار)",
        short_name="فصل العملات",
        description="فصل كشف حساب الصيدلية إلى ملفين: ليرة سورية جديدة ودولار، مع إجمالي كل عملة.",
        icon="bi-currency-exchange",
        url_name="account_statement:index",
        color="#4338ca",
    ),
    ModuleDef(
        code="compensation",
        name="تعويضات فيتا فارما",
        short_name="التعويضات",
        description="معالجة الحركة اليومية للمرتجعات والعروض واحتساب الإفرادي والسعر الإجمالي حسب المادة.",
        icon="bi-box-seam",
        url_name="compensation:index",
        color="#b91c1c",
    ),
    ModuleDef(
        code="external_commissions",
        name="عمولات الموزعين الخارجيين",
        short_name="عمولات خارجية",
        description="احتساب عمولة كل موزع خارجي 3% على (المبيعات + المرتجعات - البيانات) مع ترحيل الرصيد الدوّار.",
        icon="bi-truck",
        url_name="external_commissions:index",
        color="#0e7490",
    ),
]

MODULES_BY_CODE = {m.code: m for m in MODULES}
