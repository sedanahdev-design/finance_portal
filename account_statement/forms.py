from django import forms


class StatementUploadForm(forms.Form):
    statement_file = forms.FileField(
        label="ملف كشف حساب الصيدلية",
        widget=forms.ClearableFileInput(attrs={"class": "form-control", "accept": ".xlsx,.xls"}),
    )
