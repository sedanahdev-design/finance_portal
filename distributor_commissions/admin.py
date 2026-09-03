from django.contrib import admin

from distributor_commissions.models import DistributorCommissionRun


@admin.register(DistributorCommissionRun)
class DistributorCommissionRunAdmin(admin.ModelAdmin):
    list_display = ("id", "created_by", "created_at", "distributors_count", "rows_count", "total_commission")
