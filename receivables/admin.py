from django.contrib import admin

from receivables.models import ReceivablesRun


@admin.register(ReceivablesRun)
class ReceivablesRunAdmin(admin.ModelAdmin):
    list_display = ("id", "created_by", "created_at", "groups_count", "matched_groups", "mismatched_groups")
