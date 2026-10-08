from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("", include("core.urls")),
    path("reconciliation-hs/", include("reconciliation_hs.urls")),
    path("commissions/", include("commissions.urls")),
    path("distributor-commissions/", include("distributor_commissions.urls")),
    path("data-cleaning/", include("data_cleaning.urls")),
    path("tax-inventory/", include("tax_inventory.urls")),
    path("dawak-compare/", include("dawak_compare.urls")),
    path("account-statement/", include("account_statement.urls")),
    path("compensation/", include("compensation.urls")),
    path("external-commissions/", include("external_commissions.urls")),
    path("argivit-compare/", include("argivit_compare.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
