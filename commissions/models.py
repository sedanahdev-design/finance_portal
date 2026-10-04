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

    # ميزة "ملف الإضافات" (2026-09-27) — راتب ثابت/مرتجعات/خصم تحصيل/خصم
    # ذمم/مكافأة فيتا/سلف لكل مندوب، مدمجة مع العمولة المحسوبة لبناء
    # المستحق والصافي. انظر commissions/engine.py (merge_additions) لتوثيق
    # الصيغة الكاملة. الملف اختياري — additions_used=False يعني تشغيلاً
    # عادياً بلا هذه الميزة (شيت "نهائي" يبقى بشكله القديم تماماً).
    additions_used = models.BooleanField(default=False)
    total_due = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    total_net = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    additions_missing_count = models.IntegerField(default=0)  # عمولة محسوبة بلا صف إضافات
    additions_unmatched_count = models.IntegerField(default=0)  # صف إضافات بلا مبيعات مطابقة

    result_file = models.FileField(upload_to=upload_path, null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "عملية عمولات"
        verbose_name_plural = "عمليات العمولات"

    def __str__(self):
        return f"عمولات #{self.pk}"
