FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# مكتبات النظام اللازمة لبناء psycopg2 وتشغيل Django بشكل صحيح مع اللغة العربية
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        locales \
    && sed -i '/ar_SY/s/^# //g' /etc/locale.gen \
    && sed -i '/en_US.UTF-8/s/^# //g' /etc/locale.gen \
    && locale-gen \
    && rm -rf /var/lib/apt/lists/*

ENV LANG=C.UTF-8 \
    LC_ALL=C.UTF-8

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/media /app/staticfiles

COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
# limit-request-field_size/--limit-request-fields مرفوعتان عن افتراضي gunicorn
# (8190 بايت لكل ترويسة) كإجراء وقائي فقط ضد ترويسات Cookie كبيرة بشكل غير
# معتاد؛ السبب المعتاد لخطأ "Request Header Fields Too Large" هو تراكم كوكيز
# من مشاريع تطوير محلية أخرى على نطاق "localhost" (غير مقيد بالمنفذ) وليس
# خللاً في هذا التطبيق — يُحل من طرف المتصفح (مسح بيانات الموقع لـlocalhost).
CMD ["gunicorn", "finance_portal.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120", "--limit-request-field_size", "32760", "--limit-request-fields", "200"]
