from django.conf import settings
from django.db import models


def upload_path(instance, filename):
    return f"external_commissions/{instance.pk or 'tmp'}/{filename}"


class ExternalCommissionRun(models.Model):
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    distributors_count = models.IntegerField(default=0)
    total_debit = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    total_credit = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    total_commission = models.DecimalField(max_digits=18, decimal_places=2, default=0)

    result_file = models.FileField(upload_to=upload_path, null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "عملية عمولات موزعين خارجيين"
        verbose_name_plural = "عمليات عمولات الموزعين الخارجيين"

    def __str__(self):
        return f"عمولات موزعين خارجيين #{self.pk}"
