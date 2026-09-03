from django.contrib import admin

from reconciliation_hs.models import ReconciliationRun


@admin.register(ReconciliationRun)
class ReconciliationRunAdmin(admin.ModelAdmin):
    list_display = ("id", "created_by", "created_at", "matched_count", "hiba_only_count",
                     "sadana_only_count", "has_errors")
    list_filter = ("has_errors",)
