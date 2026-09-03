from django import forms


class DistributorCommissionUploadForm(forms.Form):
    ledger_file = forms.FileField(
        label="ملف حركة الموزعين (يحتوي شيتي «دفتر الأستاذ» و«مرتجعات»)",
        widget=forms.ClearableFileInput(attrs={"class": "form-control", "accept": ".xlsx,.xls"}),
    )
