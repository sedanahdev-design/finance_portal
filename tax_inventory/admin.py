from django.contrib import admin

from tax_inventory.models import TaxInventoryRun


@admin.register(TaxInventoryRun)
class TaxInventoryRunAdmin(admin.ModelAdmin):
    list_display = ("id", "created_by", "created_at", "items_over3", "total_final_qty")
