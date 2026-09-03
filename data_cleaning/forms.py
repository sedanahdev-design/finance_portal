from django import forms


class DataCleaningUploadForm(forms.Form):
    sales_file = forms.FileField(
        label="ملف حركة إجمالي الفواتير - مبيعات",
        widget=forms.ClearableFileInput(attrs={"class": "form-control", "accept": ".xlsx,.xls"}),
    )
    returns_file = forms.FileField(
        label="ملف حركة إجمالي الفواتير - مرتجعات",
        widget=forms.ClearableFileInput(attrs={"class": "form-control", "accept": ".xlsx,.xls"}),
    )
    discount_file = forms.FileField(
        label="ملف دفتر الحسم الممنوح",
        required=False,
        widget=forms.ClearableFileInput(attrs={"class": "form-control", "accept": ".xlsx,.xls"}),
    )
    receivables_file_1 = forms.FileField(
        label="ملف ذمم لدى قسم التوزيع",
        required=False,
        widget=forms.ClearableFileInput(attrs={"class": "form-control", "accept": ".xlsx,.xls"}),
    )
    receivables_file_2 = forms.FileField(
        label="ملف ذمم محصلة غير مقبوضة",
        required=False,
        widget=forms.ClearableFileInput(attrs={"class": "form-control", "accept": ".xlsx,.xls"}),
    )
