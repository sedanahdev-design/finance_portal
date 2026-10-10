from django import forms

# تصحيح 2026-10-10 (طلب المستخدم الصريح — راجع التوثيق الكامل في engine.py
# أعلى MOTO_NAME_OVERRIDES): خيار نوع إداري صريح لهذا التشغيل تحديداً لكل من
# "مراد علوش" و"كريم هاشم" (سائقا دراجة دائماً تلقائياً، إلا حين تقرر الإدارة
# تبديل أحدهما لسائق سيارة هذا الشهر). "تلقائي" = السلوك القديم بلا تغيير.
TIER_OVERRIDE_CHOICES = [
    ("auto", "تلقائي (حسب العمود الذي يظهر فيه بكل حركة — الافتراضي)"),
    ("moto", "سائق دراجة لكل حالاته هذا التشغيل"),
    ("car", "سائق سيارة لكل حالاته هذا التشغيل"),
]


class DistributorCommissionUploadForm(forms.Form):
    ledger_file = forms.FileField(
        label="ملف حركة الموزعين (يحتوي شيتي «دفتر الأستاذ» و«مرتجعات»)",
        widget=forms.ClearableFileInput(attrs={"class": "form-control", "accept": ".xlsx,.xls"}),
    )
    # ميزة اختيارية جديدة 2026-10-08 (طلب المستخدم الصريح: "بدي منك تضيفو ك
    # ميزة اختيارية ضمن خدمة عمولة موزعين داخليين وتتعامل مع هالملف معاملة
    # المرتجعات للموزعين") — ملف "إجمالي الفواتير"/إعادة التوزيع حين يصل
    # كملف مستقل بذاته بدل كونه شيتاً ضمن ملف دفتر الأستاذ (راجع التوثيق
    # في parse_distributor_file بـ engine.py).
    redistribution_file = forms.FileField(
        label="ملف إعادة توزيع الفواتير / إجمالي الفواتير (اختياري، جديد 2026-10-08)",
        required=False,
        widget=forms.ClearableFileInput(attrs={"class": "form-control", "accept": ".xlsx,.xls"}),
    )
    # ميزة اختيارية جديدة 2026-10-10 (طلب المستخدم الصريح: "بدي يكون عندي اسم
    # هالموزعين الاثنين بصفحة عمولات الموزعين الداخليين ويكون في عنا لكل واحد
    # منهم اختيارين واحد سائق دراجة وواحد سائق سيارة ... يحتسبلو كل الحالات
    # ... على انو سائق دراجة اذا تم اختيارها او سائق سيارة اذا تم اختيارها").
    murad_alloush_tier = forms.ChoiceField(
        label="نوع مراد علوش لهذا التشغيل",
        choices=TIER_OVERRIDE_CHOICES, initial="auto", required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    kareem_hashem_tier = forms.ChoiceField(
        label="نوع كريم هاشم لهذا التشغيل",
        choices=TIER_OVERRIDE_CHOICES, initial="auto", required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
