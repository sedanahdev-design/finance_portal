from django.conf import settings
from django.db import models


def upload_path(instance, filename):
    return f"tax_inventory/{instance.pk or 'tmp'}/{filename}"


class TaxInventoryRun(models.Model):
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    over3_file_name = models.CharField(max_length=255)
    under3_file_name = models.CharField(max_length=255)
    sales_file_name = models.CharField(max_length=255)

    items_over3 = models.IntegerField(default=0)
    items_matched_in_sales = models.IntegerField(default=0)
    total_inventory_qty = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    total_sold_qty = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    total_final_qty = models.IntegerField(default=0)
    cross_listed_count = models.IntegerField(default=0)
    capped_items_count = models.IntegerField(default=0)
    approx_items_count = models.IntegerField(default=0)

    result_file = models.FileField(upload_to=upload_path, null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "عملية مطابقة جرد"
        verbose_name_plural = "عمليات مطابقة الجرد"

    def __str__(self):
        return f"مطابقة جرد #{self.pk}"
