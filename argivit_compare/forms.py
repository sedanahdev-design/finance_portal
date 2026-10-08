from decimal import Decimal

from django import forms

RATE_MODE_CHOICES = [("fixed", "ثابت (رقم تعادل واحد)"), ("range", "متغير (نطاق بين حد أدنى وحد أعلى)")]


class ArgivitCompareUploadForm(forms.Form):
    movement_file = forms.FileField(
        label="ملف الحركة اليومية (مفرق) — بيع ومرتجع الارجيفيت بالليرة",
        widget=forms.ClearableFileInput(attrs={"class": "form-control", "accept": ".xlsx,.xls"}),
    )
    price_file = forms.FileField(
        label="ملف قائمة أسعار الارجيفيت بالدولار",
        widget=forms.ClearableFileInput(attrs={"class": "form-control", "accept": ".xlsx,.xls"}),
    )
    ledger_file = forms.FileField(
        label="ملف دفتر الأستاذ (مواد دولار — لمعرفة سعر الصرف الفعلي لكل فاتورة فقط)",
        widget=forms.ClearableFileInput(attrs={"class": "form-control", "accept": ".xlsx,.xls"}),
    )
    wholesale_file = forms.FileField(
        label="ملف مبيعات الجملة مع المرتجعات (اختياري — لتشغيل مطابقة بيع/مرتجع الجملة أيضاً)",
        required=False,
        widget=forms.ClearableFileInput(attrs={"class": "form-control", "accept": ".xlsx,.xls"}),
    )

    rate_mode = forms.ChoiceField(
        label="نمط سعر الصرف",
        choices=RATE_MODE_CHOICES, initial="fixed",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    rate_fixed = forms.DecimalField(
        label="سعر الصرف الثابت (ليرة لكل دولار)", required=False, min_value=Decimal("0.0001"),
        widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "placeholder": "مثال: 135"}),
    )
    rate_min = forms.DecimalField(
        label="سعر الصرف — الحد الأدنى", required=False, min_value=Decimal("0.0001"),
        widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "placeholder": "مثال: 133"}),
    )
    rate_max = forms.DecimalField(
        label="سعر الصرف — الحد الأعلى", required=False, min_value=Decimal("0.0001"),
        widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "placeholder": "مثال: 140"}),
    )

    def clean(self):
        cleaned = super().clean()
        mode = cleaned.get("rate_mode")
        if mode == "fixed":
            if not cleaned.get("rate_fixed"):
                self.add_error("rate_fixed", "مطلوب عند اختيار نمط 'ثابت'.")
        elif mode == "range":
            lo, hi = cleaned.get("rate_min"), cleaned.get("rate_max")
            if not lo or not hi:
                self.add_error("rate_min", "مطلوب عند اختيار نمط 'متغير' (الحد الأدنى والحد الأعلى معاً).")
            elif lo > hi:
                self.add_error("rate_min", "الحد الأدنى يجب أن يكون أصغر من أو يساوي الحد الأعلى.")
        return cleaned
