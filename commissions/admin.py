from django.contrib import admin

from commissions.models import CommissionRun


@admin.register(CommissionRun)
class CommissionRunAdmin(admin.ModelAdmin):
    list_display = ("id", "created_by", "created_at", "reps_count", "total_sales", "total_commission")
