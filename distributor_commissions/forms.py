from django import forms


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
