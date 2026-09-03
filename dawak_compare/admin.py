from django.contrib import admin

from dawak_compare.models import DawakCompareRun


@admin.register(DawakCompareRun)
class DawakCompareRunAdmin(admin.ModelAdmin):
    list_display = ("id", "created_by", "created_at", "pharmacies_count", "matched_count", "mismatched_count")
