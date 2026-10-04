"""
Django settings for finance_portal project.

منصّة أتمتة عمليات القسم المالي.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "django-insecure-gg=eg(@*@q5&5gk4y#x140=!@^c-*$d8++&(%n1prjw&p*mvw7",
)

DEBUG = os.environ.get("DJANGO_DEBUG", "1") == "1"

ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "*").split(",")

# عند التشغيل خلف بروكسي عكسي/نفق مثل Cloudflare، يصل الطلب إلى Django عبر
# HTTP عادي داخلياً حتى لو كان المستخدم يتصفح https فعلياً، وDjango يرفض
# طلبات تسجيل الدخول/POST بخطأ "CSRF verification failed" لأنه لا يعرف أن
# الطلب أصلاً كان آمناً (https)، ولأنه لا "يثق" تلقائياً بنطاق خارجي جديد.
# السطران التاليان يحلّان هذا:
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

CSRF_TRUSTED_ORIGINS = [
    o.strip() for o in os.environ.get("DJANGO_CSRF_TRUSTED_ORIGINS", "").split(",") if o.strip()
]

# دعم مدمج لأنفاق Cloudflare السريعة (trycloudflare.com) للاختبار السريع.
# هذه الأنفاق تعطي رابطاً عشوائياً مختلفاً في كل مرة يُعاد تشغيلها، لذلك لا
# فائدة من وضع رابط محدد في DJANGO_CSRF_TRUSTED_ORIGINS (سيصبح قديماً فوراً).
# بدلاً من ذلك نُثق بنطاق trycloudflare.com الفرعي كاملاً (وهو نطاق ثابت
# تملكه Cloudflare نفسها، فالوثوق به آمن ولا يفتح الباب لأي نطاق آخر).
# يمكن تعطيل هذا بوضع DJANGO_TRUST_CLOUDFLARE_TUNNEL=0 في البيئة.
if os.environ.get("DJANGO_TRUST_CLOUDFLARE_TUNNEL", "1") == "1":
    CSRF_TRUSTED_ORIGINS.append("https://*.trycloudflare.com")
    # لا يكفي وحدها CSRF_TRUSTED_ORIGINS: يجب أيضاً أن يقبل ALLOWED_HOSTS نطاق
    # الرابط، وإلا رفض Django كل طلب برسالة "Bad Request (400)" بسبب رأس
    # Host غير معروف — حتى لو كانت DJANGO_ALLOWED_HOSTS في البيئة مضبوطة على
    # نطاق آخر محدد. القيمة التي تبدأ بنقطة تعني "هذا النطاق وأي نطاق فرعي له".
    if ".trycloudflare.com" not in ALLOWED_HOSTS and "*" not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(".trycloudflare.com")


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",

    # التطبيق الأساسي (المستخدمون، الصلاحيات، سجل التدقيق، الواجهة العامة)
    "core",

    # تطبيقات الحلول (أُلغيت وحدة "مطابقة الذمم مع قسم التوزيع" نهائياً بتاريخ 2026-10-01 بطلب صريح من المستخدم لعدم فعاليتها)
    "reconciliation_hs",       # 1) مطابقة هبة - سدانة
    "commissions",             # 2أ) عمولات المندوبين
    "distributor_commissions", # 2ب) عمولة تحصيل الموزعين الداخليين
    "data_cleaning",           # 3) تنظيف داتا
    "tax_inventory",           # 4) مطابقة جرد الضريبة
    "dawak_compare",           # 6) مطابقة دواك
    "account_statement",       # 7) فصل كشف الحساب (ليرة / دولار)
    "compensation",            # 8) تعويضات فيتا فارما
    "external_commissions",    # 9) عمولات الموزعين الخارجيين
    "argivit_compare",         # 10) مطابقة أسعار الارجيفيت والمبيعات مع المرتجعات (أُضيفت 2026-10-01)
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "core.middleware.AuditLogMiddleware",
]

ROOT_URLCONF = "finance_portal.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.context_processors.modules_nav",
            ],
        },
    },
]

WSGI_APPLICATION = "finance_portal.wsgi.application"


# قاعدة البيانات: PostgreSQL
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("DB_NAME", "finance_portal"),
        "USER": os.environ.get("DB_USER", "finance_admin"),
        "PASSWORD": os.environ.get("DB_PASSWORD", "finance_dev_pw"),
        "HOST": os.environ.get("DB_HOST", "127.0.0.1"),
        "PORT": os.environ.get("DB_PORT", "5432"),
    }
}

AUTH_USER_MODEL = "core.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 8}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# اللغة والتوقيت
LANGUAGE_CODE = "ar"
TIME_ZONE = "Asia/Damascus"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}
# بعض ملفات المكتبات المُجهَّزة مسبقاً (مثل bootstrap.rtl.min.css) تشير إلى
# ملفات خرائط مصدر (.map) غير مرفقة؛ هذا لا يؤثر على عمل الموقع، لذلك لا
# نفشل عملية collectstatic بسببها.
WHITENOISE_MANIFEST_STRICT = False

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = "core:login"
LOGIN_REDIRECT_URL = "core:dashboard"
LOGOUT_REDIRECT_URL = "core:login"

# حجم أقصى لملفات الإكسل المرفوعة (ميغابايت) قبل أن تُكتب مؤقتاً على القرص
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024
DATA_UPLOAD_MAX_MEMORY_SIZE = 25 * 1024 * 1024

MESSAGE_TAGS = {}
