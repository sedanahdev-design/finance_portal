#!/bin/sh
set -e

echo "==> انتظار قاعدة البيانات..."
python3 - <<'PYEOF'
import os
import sys
import time

import psycopg2

host = os.environ.get("DB_HOST", "db")
port = os.environ.get("DB_PORT", "5432")
name = os.environ.get("DB_NAME", "finance_portal")
user = os.environ.get("DB_USER", "finance_admin")
password = os.environ.get("DB_PASSWORD", "finance_dev_pw")

for attempt in range(60):
    try:
        conn = psycopg2.connect(host=host, port=port, dbname=name, user=user, password=password)
        conn.close()
        print("==> قاعدة البيانات جاهزة.")
        sys.exit(0)
    except psycopg2.OperationalError:
        time.sleep(1)

print("==> تعذّر الاتصال بقاعدة البيانات بعد عدة محاولات.")
sys.exit(1)
PYEOF

echo "==> تطبيق الترحيلات (migrate)..."
python3 manage.py migrate --noinput

echo "==> تجميع الملفات الثابتة (collectstatic)..."
python3 manage.py collectstatic --noinput

if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
    echo "==> إنشاء/تحديث المستخدم المشرف الافتراضي..."
    python3 manage.py shell -c "
from core.models import User
username = '$DJANGO_SUPERUSER_USERNAME'
password = '$DJANGO_SUPERUSER_PASSWORD'
email = '${DJANGO_SUPERUSER_EMAIL:-admin@example.com}'
user, created = User.objects.get_or_create(username=username, defaults={'email': email, 'role': User.Role.SUPERVISOR})
user.is_staff = True
user.is_superuser = True
user.role = User.Role.SUPERVISOR
user.set_password(password)
user.save()
print('تم الإنشاء' if created else 'تم التحديث')
" || true
fi

echo "==> تشغيل الخادم..."
exec "$@"
