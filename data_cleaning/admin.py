from django.contrib import admin

from data_cleaning.models import DataCleaningRun


@admin.register(DataCleaningRun)
class DataCleaningRunAdmin(admin.ModelAdmin):
    list_display = ("id", "created_by", "created_at", "total_rows", "sales_rows", "returns_rows")
