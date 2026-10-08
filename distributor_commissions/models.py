from django.conf import settings
from django.db import models


def upload_path(instance, filename):
    return f"distributor_commissions/{instance.pk or 'tmp'}/{filename}"


class DistributorCommissionRun(models.Model):
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    ledger_file_name = models.CharField(max_length=255, blank=True)
    distributors_count = models.IntegerField(default=0)
    rows_count = models.IntegerField(default=0)
    return_rows_count = models.IntegerField(default=0)
    total_debit = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    total_commission = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    collection_total = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    return_total = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    flagged_rows_count = models.IntegerField(default=0)
    # حركات "الحساب المقابل" يحوي كلمة "مستودع" — تُستبعد كلياً من العمولة.
    # تحقّق 2026-08-31: صيغ شيت "تقرير نتيجة " المرجعي (بلا data_only) تؤكد
    # أن 5 من 6 حالات فعلية في الملف المرجعي مُصفَّرة يدوياً فعلاً (قيم ثابتة
    # لا صيغ) — القاعدة صحيحة. الاستثناء الوحيد (سليم العبد، سند 142153)
    # الأرجح أنه سهو فردي في إعداد الملف المرجعي، موثَّق ومُبلَّغ للمستخدم.
    warehouse_excluded_count = models.IntegerField(default=0)

    # تصحيح 2026-09-28 (طلب المستخدم الصريح) — انظر توثيق الحالتين في
    # distributor_commissions/engine.py (parse_distributor_file):
    #  - fuzzy_biyad_rows_count: حركات فيها مشارك استُخرج اسمه من نص البيان
    #    بمطابقة تقريبية فقط (كنية/خطأ إملائي) — محتسَبة طبيعياً لكن تحتاج
    #    تأكيداً يدوياً (لوّنت برتقالياً).
    #  - unresolved_rows_count: حركات (تحصيل أو مرتجع) بلا أي موزع معروف
    #    إطلاقاً — سابقاً كانت تُحذف صامتة، الآن تظهر بشيت مخصص أحمر بدل
    #    ذلك، بلا احتساب عمولة لها.
    fuzzy_biyad_rows_count = models.IntegerField(default=0)
    unresolved_rows_count = models.IntegerField(default=0)

    result_file = models.FileField(upload_to=upload_path, null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "عملية عمولة تحصيل موزعين"
        verbose_name_plural = "عمليات عمولة تحصيل الموزعين"

    def __str__(self):
        return f"عمولة تحصيل موزعين #{self.pk}"
