from django import forms


class DawakCompareUploadForm(forms.Form):
    dawak_file = forms.FileField(
        label="ملف مشروع دواك",
        widget=forms.ClearableFileInput(attrs={"class": "form-control", "accept": ".xlsx,.xls"}),
    )
    hiba_file = forms.FileField(
        label="ملف كشف حساب هبة",
        widget=forms.ClearableFileInput(attrs={"class": "form-control", "accept": ".xlsx,.xls"}),
    )
