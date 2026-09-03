from django.contrib import admin

from account_statement.models import StatementSplitRun


@admin.register(StatementSplitRun)
class StatementSplitRunAdmin(admin.ModelAdmin):
    list_display = ("id", "created_by", "created_at", "source_file_name", "total_rows")
