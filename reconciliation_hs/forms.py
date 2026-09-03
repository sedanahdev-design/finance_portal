from django import forms


class ReconciliationUploadForm(forms.Form):
    sadana_file = forms.FileField(
        label="ملف سدانة",
        widget=forms.ClearableFileInput(attrs={"class": "form-control", "accept": ".xlsx,.xls"}),
    )
    hiba_file = forms.FileField(
        label="ملف هبة",
        widget=forms.ClearableFileInput(attrs={"class": "form-control", "accept": ".xlsx,.xls"}),
    )

    def clean(self):
        cleaned = super().clean()
        for field in ("sadana_file", "hiba_file"):
            f = cleaned.get(field)
            if f and not f.name.lower().endswith((".xlsx", ".xls")):
                self.add_error(field, "الرجاء رفع ملف إكسل بصيغة xlsx أو xls فقط.")
        return cleaned
