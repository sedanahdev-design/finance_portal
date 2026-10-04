from django.conf import settings
from django.db import models


def upload_path(instance, filename):
    return f"compensation/{instance.pk or 'tmp'}/{filename}"


class CompensationRun(models.Model):
    """نتيجة عملية تعويضات فيتا فارما — أُعيد بناء منطق الحساب مرتين
    بطلب المستخدم الصريح (2026-08-30 ثم 2026-08-31)، بخطوات حرفية زوّدنا
    بها في كل مرة، مع تحقق رقمي مباشر من ملف مرجعي حقيقي مبني يدوياً في
    كل خطوة. النسخة الحالية (2026-08-31 الثانية): التجميع على مستوى
    (مادة × عرض مفرق) بلا زبون، والمعادلة على مستوى كل سطر بمفرده. انظر
    شرح كامل في compensation/engine.py."""

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    source_file_name = models.CharField(max_length=255)

    raw_row_count = models.IntegerField(default=0)
    # عدد الأسطر التي اجتازت فلتر "العروض المميزة فقط" (الخطوة 2 في engine.py)
    offer_row_count = models.IntegerField(default=0)
    # عدد المواد المستبعدة بالكامل لعدم وجود أي عرض مميز لها في كل الملف
    ignored_items_count = models.IntegerField(default=0)
    # فواتير "م. مبيع" المستبعدة بمفردها (بلا زوج بيع مطابق) — تحقّق 2026-08-31
    excluded_mabee_rows_count = models.IntegerField(default=0)
    # أزواج (سطر "م. مبيع" + سطر بيع مطابق بنفس الزبون) أُلغيت معاً
    cancelled_mabee_pairs = models.IntegerField(default=0)
    cancelled_pairs = models.IntegerField(default=0)
    unmatched_returns_count = models.IntegerField(default=0)
    # أسطر كان صافيها (الهدايا − ناتج معادلة السطر) سالباً أو صفرياً — حُذفت
    # بالكامل من الحساب بطلب المستخدم الصريح (تصحيح 2026-08-31 الثاني)
    excluded_nonpositive_rows_count = models.IntegerField(default=0)
    # أسطر كمية=صفر دُمجت هداياها مع سطر آخر لنفس الزبون ثم حُذفت (تصحيح
    # 2026-08-31 الثالث، بمثال بالصور)
    merged_zero_qty_rows_count = models.IntegerField(default=0)
    # أسطر كمية=صفر بلا سطر آخر لنفس الزبون لدمج هداياها معه — بقيت وحدها
    unmerged_zero_qty_rows_count = models.IntegerField(default=0)
    # تعديل 2026-10-04: سطر "م. مبيع"/مرتجع كبير الحجم (بلا فاتورة بيع
    # واحدة تطابقه تماماً) أُلغي مقابل تجميع عدة فواتير بيع أصغر — راجع
    # الشرح الكامل (حالة "100+80" الحقيقية) في compensation/engine.py
    pool_matches_count = models.IntegerField(default=0)
    pool_matched_rows_count = models.IntegerField(default=0)

    items_count = models.IntegerField(default=0)
    # عدد الحزم (مادة × عرض مفرق) — مستوى التجميع والنتيجة النهائي (بلا زبون)
    groups_count = models.IntegerField(default=0)
    # حزم بلا قيمة "عرض مفرق" صالحة — تعذّر تطبيق المعادلة عليها
    ineligible_groups_count = models.IntegerField(default=0)

    total_qty = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    total_gifts = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    # ناتج المعادلة وحده (قبل طرحه من الهدايا) — الخطوة 8 في engine.py
    total_formula_result = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    # المطالبة النهائية = مجموع الهدايا − ناتج المعادلة — الخطوة 9 في engine.py
    total_claim_value = models.DecimalField(max_digits=18, decimal_places=2, default=0)

    result_file = models.FileField(upload_to=upload_path, null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "عملية تعويضات فيتا فارما"
        verbose_name_plural = "عمليات تعويضات فيتا فارما"

    def __str__(self):
        return f"تعويضات فيتا فارما #{self.pk}"
