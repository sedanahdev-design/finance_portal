from django.contrib.auth.models import AbstractUser
from django.db import models

from core.module_registry import MODULES


class User(AbstractUser):
    """مستخدم النظام: مشرف القسم المالي أو أحد موظفي القسم."""

    class Role(models.TextChoices):
        SUPERVISOR = "supervisor", "مشرف القسم"
        STAFF = "staff", "موظف"

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.STAFF)
    phone = models.CharField(max_length=30, blank=True)
    job_title = models.CharField(max_length=120, blank=True, verbose_name="المسمى الوظيفي")
    is_active_employee = models.BooleanField(default=True, verbose_name="موظف فعّال")

    class Meta:
        verbose_name = "مستخدم"
        verbose_name_plural = "المستخدمون"

    def __str__(self):
        return self.get_full_name() or self.username

    @property
    def is_supervisor(self):
        return self.role == self.Role.SUPERVISOR or self.is_superuser

    def accessible_module_codes(self):
        """أكواد الوحدات المسموح لهذا المستخدم بالوصول إليها."""
        if self.is_supervisor:
            return {m.code for m in MODULES}
        return set(
            self.module_access.filter(can_view=True).values_list("module_code", flat=True)
        )

    def can_access(self, module_code):
        if self.is_supervisor:
            return True
        return self.module_access.filter(module_code=module_code, can_view=True).exists()

    def can_edit(self, module_code):
        if self.is_supervisor:
            return True
        return self.module_access.filter(module_code=module_code, can_edit=True).exists()


class ModuleAccess(models.Model):
    """صلاحية مستخدم واحد على وحدة واحدة من الحلول التسعة."""

    MODULE_CHOICES = [(m.code, m.name) for m in MODULES]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="module_access")
    module_code = models.CharField(max_length=50, choices=MODULE_CHOICES)
    can_view = models.BooleanField(default=True, verbose_name="عرض")
    can_edit = models.BooleanField(default=True, verbose_name="رفع/تشغيل")
    can_export = models.BooleanField(default=True, verbose_name="تصدير النتائج")
    granted_at = models.DateTimeField(auto_now_add=True)
    granted_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )

    class Meta:
        unique_together = [("user", "module_code")]
        verbose_name = "صلاحية وحدة"
        verbose_name_plural = "صلاحيات الوحدات"

    def __str__(self):
        return f"{self.user} → {self.get_module_code_display()}"


class AuditLog(models.Model):
    """سجل تدقيق لكل عملية مهمة (رفع ملف، تشغيل مطابقة، تصدير نتيجة) لضمان إمكانية التتبع."""

    class Action(models.TextChoices):
        LOGIN = "login", "تسجيل دخول"
        UPLOAD = "upload", "رفع ملف"
        RUN = "run", "تشغيل عملية"
        EXPORT = "export", "تصدير نتيجة"
        VIEW = "view", "عرض"
        ADMIN = "admin", "إدارة مستخدمين"
        ERROR = "error", "خطأ"

    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name="audit_logs")
    module_code = models.CharField(max_length=50, blank=True)
    action = models.CharField(max_length=20, choices=Action.choices)
    message = models.CharField(max_length=500)
    meta = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "سجل تدقيق"
        verbose_name_plural = "سجلات التدقيق"

    def __str__(self):
        return f"[{self.created_at:%Y-%m-%d %H:%M}] {self.user} - {self.message}"
