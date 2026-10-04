from django.conf import settings
from django.db import models


def upload_path(instance, filename):
    return f"argivit_compare/{instance.pk or 'tmp'}/{filename}"


class ArgivitCompareRun(models.Model):
    """نتيجة عملية مطابقة أسعار الارجيفيت (بالدولار) والمبيعات مع
    المرتجعات — بُنيت 2026-10-01 بطلب صريح من المستخدم. انظر شرح كامل
    للمنهجية وقرارات التصميم في argivit_compare/engine.py."""

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    movement_file_name = models.CharField(max_length=255)
    price_file_name = models.CharField(max_length=255)
    ledger_file_name = models.CharField(max_length=255)
    wholesale_file_name = models.CharField(max_length=255, blank=True, default="")

    rate_mode = models.CharField(max_length=10, default="fixed")  # fixed أو range
    rate_lo = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    rate_hi = models.DecimalField(max_digits=10, decimal_places=4, default=0)

    movement_rows_count = models.IntegerField(default=0)
    tier1_count = models.IntegerField(default=0)
    tier2_count = models.IntegerField(default=0)
    tier3_count = models.IntegerField(default=0)
    tier4_count = models.IntegerField(default=0)
    unmatched_count = models.IntegerField(default=0)

    retail_matched_count = models.IntegerField(default=0)
    retail_mismatched_count = models.IntegerField(default=0)
    retail_no_counterpart_count = models.IntegerField(default=0)
    wholesale_matched_count = models.IntegerField(default=0)
    wholesale_mismatched_count = models.IntegerField(default=0)
    wholesale_no_counterpart_count = models.IntegerField(default=0)

    result_file = models.FileField(upload_to=upload_path, null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "عملية مطابقة أسعار الارجيفيت"
        verbose_name_plural = "عمليات مطابقة أسعار الارجيفيت"

    def __str__(self):
        return f"مطابقة أسعار الارجيفيت #{self.pk}"
