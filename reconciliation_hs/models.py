from django.conf import settings
from django.db import models


def upload_path(instance, filename):
    return f"reconciliation_hs/{instance.pk or 'tmp'}/{filename}"


class ReconciliationRun(models.Model):
    """عملية مطابقة واحدة بين ملف هبة وملف سدانة."""

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    hiba_file_name = models.CharField(max_length=255)
    sadana_file_name = models.CharField(max_length=255)

    hiba_count = models.IntegerField(default=0)
    sadana_count = models.IntegerField(default=0)
    matched_count = models.IntegerField(default=0)
    matched_same_day = models.IntegerField(default=0)
    matched_date_diff = models.IntegerField(default=0)
    hiba_only_count = models.IntegerField(default=0)
    sadana_only_count = models.IntegerField(default=0)
    hiba_only_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    sadana_only_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)

    found_diff_date_count = models.IntegerField(default=0)
    found_diff_date_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)

    hiba_period_start = models.DateField(null=True, blank=True)
    hiba_period_end = models.DateField(null=True, blank=True)
    sadana_period_start = models.DateField(null=True, blank=True)
    sadana_period_end = models.DateField(null=True, blank=True)

    has_errors = models.BooleanField(default=False)
    result_file = models.FileField(upload_to=upload_path, null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "عملية مطابقة"
        verbose_name_plural = "عمليات المطابقة"

    def __str__(self):
        return f"مطابقة #{self.pk} — {self.created_at:%Y-%m-%d %H:%M}"

    @property
    def match_rate(self):
        total = self.hiba_count + self.sadana_count
        if not total:
            return 0
        return round((self.matched_count * 2) / total * 100, 1)
