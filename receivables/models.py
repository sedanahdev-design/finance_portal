from django.conf import settings
from django.db import models


def upload_path(instance, filename):
    return f"receivables/{instance.pk or 'tmp'}/{filename}"


class ReceivablesRun(models.Model):
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    source_file_name = models.CharField(max_length=255)

    total_rows = models.IntegerField(default=0)
    linked_rows = models.IntegerField(default=0)
    unlinked_rows = models.IntegerField(default=0)
    groups_count = models.IntegerField(default=0)
    matched_groups = models.IntegerField(default=0)
    mismatched_groups = models.IntegerField(default=0)
    mismatched_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)

    # تصحيح 2026-09-29 (ميزة "مطابقة حسب الكشف + تفصيل حسب الشخص" الجديدة،
    # طلب المستخدم الصريح): إحصاءات إضافية للتمييز بين المجموعات "الفردية"
    # و"المشتركة" بين أكثر من موزّع، والمجموعات المرتبطة بالاسم فقط (بلا رقم
    # كشف)، وعدد الأشخاص (الموزّعين) الظاهرين في الملف.
    solo_mismatched_groups = models.IntegerField(default=0)
    shared_mismatched_groups = models.IntegerField(default=0)
    name_linked_groups = models.IntegerField(default=0)
    persons_count = models.IntegerField(default=0)

    result_file = models.FileField(upload_to=upload_path, null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "عملية مطابقة ذمم"
        verbose_name_plural = "عمليات مطابقة الذمم"

    def __str__(self):
        return f"مطابقة ذمم #{self.pk}"
