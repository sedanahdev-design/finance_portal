from django.contrib import admin

from external_commissions.models import ExternalCommissionRun


@admin.register(ExternalCommissionRun)
class ExternalCommissionRunAdmin(admin.ModelAdmin):
    list_display = ("id", "created_by", "created_at", "distributors_count", "total_commission")
