from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from core.models import AuditLog, ModuleAccess, User


class ModuleAccessInline(admin.TabularInline):
    model = ModuleAccess
    extra = 0
    fk_name = "user"


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    inlines = [ModuleAccessInline]
    list_display = ("username", "get_full_name", "role", "job_title", "is_active", "is_active_employee")
    list_filter = ("role", "is_active", "is_active_employee")
    fieldsets = UserAdmin.fieldsets + (
        ("بيانات القسم المالي", {"fields": ("role", "phone", "job_title", "is_active_employee")}),
    )


@admin.register(ModuleAccess)
class ModuleAccessAdmin(admin.ModelAdmin):
    list_display = ("user", "module_code", "can_view", "can_edit", "can_export", "granted_at")
    list_filter = ("module_code", "can_view", "can_edit")


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("created_at", "user", "action", "module_code", "message")
    list_filter = ("action", "module_code")
    search_fields = ("message", "user__username")
    date_hierarchy = "created_at"
