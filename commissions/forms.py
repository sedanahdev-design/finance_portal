from django import forms


class CommissionUploadForm(forms.Form):
    sales_file = forms.FileField(
        label="ملف الحركة اليومية - مبيعات المندوبين",
        widget=forms.ClearableFileInput(attrs={"class": "form-control", "accept": ".xlsx,.xls"}),
    )
    returns_file = forms.FileField(
        label="ملف الحركة اليومية - مرتجعات المندوبين",
        widget=forms.ClearableFileInput(attrs={"class": "form-control", "accept": ".xlsx,.xls"}),
    )
    rates_file = forms.FileField(
        label="ملف نسب العمولات",
        widget=forms.ClearableFileInput(attrs={"class": "form-control", "accept": ".xlsx,.xls"}),
    )
    sanitizer_targets_file = forms.FileField(
        label="ملف تارغت المعقمات",
        required=False,
        widget=forms.ClearableFileInput(attrs={"class": "form-control", "accept": ".xlsx,.xls"}),
    )
    additions_file = forms.FileField(
        label="ملف الإضافات (راتب ثابت/مرتجعات/خصم تحصيل/خصم ذمم/مكافأة فيتا/سلف)",
        required=False,
        widget=forms.ClearableFileInput(attrs={"class": "form-control", "accept": ".xlsx,.xls"}),
    )
