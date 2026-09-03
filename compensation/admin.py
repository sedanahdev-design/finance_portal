from django.contrib import admin

from compensation.models import CompensationRun


@admin.register(CompensationRun)
class CompensationRunAdmin(admin.ModelAdmin):
    list_display = ("id", "created_by", "created_at", "items_count", "groups_count", "ignored_items_count", "ineligible_groups_count", "total_claim_value")
