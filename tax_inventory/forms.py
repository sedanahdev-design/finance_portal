from django import forms


class TaxInventoryUploadForm(forms.Form):
    over3_file = forms.FileField(
        label="ملف جرد المواد فوق 3 قطع (أمين 9 — السقف)",
        widget=forms.ClearableFileInput(attrs={"class": "form-control", "accept": ".xlsx,.xls"}),
    )
    under3_file = forms.FileField(
        label="ملف جرد المواد تحت 3 قطع (فحص إعلامي فقط)",
        widget=forms.ClearableFileInput(attrs={"class": "form-control", "accept": ".xlsx,.xls"}),
    )
    sales_file = forms.FileField(
        label="ملف حركة المبيعات (أمين 8 — التفصيل الحقيقي حسب الصيدلية)",
        widget=forms.ClearableFileInput(attrs={"class": "form-control", "accept": ".xlsx,.xls"}),
    )
