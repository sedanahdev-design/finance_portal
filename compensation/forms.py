from django import forms


class CompensationUploadForm(forms.Form):
    movement_file = forms.FileField(
        label="ملف الحركة اليومية والمطالبات (تعويضات فيتا فارما)",
        widget=forms.ClearableFileInput(attrs={"class": "form-control", "accept": ".xlsx,.xls"}),
    )
