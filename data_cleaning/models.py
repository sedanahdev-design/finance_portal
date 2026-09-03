from django.conf import settings
from django.db import models


def upload_path(instance, filename):
    return f"data_cleaning/{instance.pk or 'tmp'}/{filename}"


class DataCleaningRun(models.Model):
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    total_rows = models.IntegerField(default=0)
    sales_rows = models.IntegerField(default=0)
    returns_rows = models.IntegerField(default=0)
    receivables_rows = models.IntegerField(default=0)
    discount_rows = models.IntegerField(default=0)
    total_deferred_value = models.DecimalField(max_digits=18, decimal_places=2, default=0)

    result_file = models.FileField(upload_to=upload_path, null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "عملية تنظيف داتا"
        verbose_name_plural = "عمليات تنظيف الداتا"

    def __str__(self):
        return f"تنظيف داتا #{self.pk}"
