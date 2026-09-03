from django.conf import settings
from django.db import models


def upload_path(instance, filename):
    return f"commissions/{instance.pk or 'tmp'}/{filename}"


class CommissionRun(models.Model):
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    reps_count = models.IntegerField(default=0)
    total_sales = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    total_commission = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    unrated_companies_count = models.IntegerField(default=0)

    result_file = models.FileField(upload_to=upload_path, null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "عملية عمولات"
        verbose_name_plural = "عمليات العمولات"

    def __str__(self):
        return f"عمولات #{self.pk}"
