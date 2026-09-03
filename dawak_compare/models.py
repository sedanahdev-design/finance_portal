from django.conf import settings
from django.db import models


def upload_path(instance, filename):
    return f"dawak_compare/{instance.pk or 'tmp'}/{filename}"


class DawakCompareRun(models.Model):
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    dawak_file_name = models.CharField(max_length=255)
    hiba_file_name = models.CharField(max_length=255)

    pharmacies_count = models.IntegerField(default=0)
    matched_count = models.IntegerField(default=0)
    mismatched_count = models.IntegerField(default=0)
    mismatched_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    hiba_balance = models.DecimalField(max_digits=18, decimal_places=2, default=0)

    # مطابقة الدفعات دواك⇄هبة على مستوى الحركة الفردية (وليس إجمالي الصيدلية فقط)
    payments_dawak_count = models.IntegerField(default=0)
    payments_hiba_count = models.IntegerField(default=0)
    payments_matched_count = models.IntegerField(default=0)
    payments_found_diff_date_count = models.IntegerField(default=0)
    payments_found_diff_date_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    payments_true_diff_count = models.IntegerField(default=0)
    payments_true_diff_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)

    result_file = models.FileField(upload_to=upload_path, null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "عملية مطابقة دواك"
        verbose_name_plural = "عمليات مطابقة دواك"

    def __str__(self):
        return f"مطابقة دواك #{self.pk}"
