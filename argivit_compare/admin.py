from django.contrib import admin

from argivit_compare.models import ArgivitCompareRun


@admin.register(ArgivitCompareRun)
class ArgivitCompareRunAdmin(admin.ModelAdmin):
    list_display = (
        "id", "created_by", "created_at", "movement_rows_count",
        "tier1_count", "tier2_count", "tier3_count", "tier4_count", "unmatched_count",
        "retail_mismatched_count", "wholesale_mismatched_count",
    )
