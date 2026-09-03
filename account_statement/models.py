from django.conf import settings
from django.db import models


def upload_path(instance, filename):
    return f"account_statement/{instance.pk or 'tmp'}/{filename}"


class StatementSplitRun(models.Model):
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    source_file_name = models.CharField(max_length=255)
    total_rows = models.IntegerField(default=0)
    summary_json = models.JSONField(default=dict, blank=True)
    result_file = models.FileField(upload_to=upload_path, null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "عملية فصل عملات"
        verbose_name_plural = "عمليات فصل العملات"

    def __str__(self):
        return f"فصل عملات #{self.pk}"
