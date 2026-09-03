from django import forms


class ReceivablesUploadForm(forms.Form):
    ledger_file = forms.FileField(
        label="ملف ذمم لدى قسم التوزيع",
        widget=forms.ClearableFileInput(attrs={"class": "form-control", "accept": ".xlsx,.xls"}),
    )
