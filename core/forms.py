from django import forms
from django.contrib.auth.forms import AuthenticationForm

from core.models import ModuleAccess, User
from core.module_registry import MODULES


class ArabicLoginForm(AuthenticationForm):
    username = forms.CharField(
        label="اسم المستخدم",
        widget=forms.TextInput(attrs={"class": "form-control", "autofocus": True, "placeholder": "اسم المستخدم"}),
    )
    password = forms.CharField(
        label="كلمة المرور",
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "كلمة المرور"}),
    )
    error_messages = {
        "invalid_login": "اسم المستخدم أو كلمة المرور غير صحيحة.",
        "inactive": "هذا الحساب غير مُفعّل.",
    }


class StaffUserForm(forms.ModelForm):
    """نموذج إنشاء/تعديل مستخدم موظف من قبل المشرف."""

    password = forms.CharField(
        label="كلمة المرور", required=False, widget=forms.PasswordInput(attrs={"class": "form-control"}),
        help_text="اتركه فارغاً عند التعديل إن لم ترغب بتغيير كلمة المرور.",
    )

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "job_title", "phone", "role", "is_active_employee"]
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "job_title": forms.TextInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "role": forms.Select(attrs={"class": "form-select"}),
            "is_active_employee": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
        labels = {
            "username": "اسم المستخدم",
            "first_name": "الاسم الأول",
            "last_name": "اسم العائلة",
            "job_title": "المسمى الوظيفي",
            "phone": "رقم الهاتف",
            "role": "الدور",
            "is_active_employee": "موظف فعّال",
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        pwd = self.cleaned_data.get("password")
        if pwd:
            user.set_password(pwd)
        elif not user.pk:
            user.set_unusable_password()
        if commit:
            user.save()
        return user


class ModuleAccessForm(forms.Form):
    """نموذج ديناميكي لضبط صلاحيات مستخدم واحد على كل الوحدات التسعة دفعة واحدة."""

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.target_user = user
        existing = {
            ma.module_code: ma
            for ma in ModuleAccess.objects.filter(user=user)
        } if user else {}
        for m in MODULES:
            ex = existing.get(m.code)
            self.fields[f"view_{m.code}"] = forms.BooleanField(
                required=False, initial=bool(ex and ex.can_view), label=m.name
            )
            self.fields[f"edit_{m.code}"] = forms.BooleanField(
                required=False, initial=bool(ex and ex.can_edit)
            )
            self.fields[f"export_{m.code}"] = forms.BooleanField(
                required=False, initial=bool(ex and ex.can_export)
            )

    def save(self, granted_by=None):
        for m in MODULES:
            view = self.cleaned_data.get(f"view_{m.code}")
            edit = self.cleaned_data.get(f"edit_{m.code}")
            export = self.cleaned_data.get(f"export_{m.code}")
            if view or edit or export:
                ModuleAccess.objects.update_or_create(
                    user=self.target_user,
                    module_code=m.code,
                    defaults={
                        "can_view": view,
                        "can_edit": edit,
                        "can_export": export,
                        "granted_by": granted_by,
                    },
                )
            else:
                ModuleAccess.objects.filter(user=self.target_user, module_code=m.code).delete()
