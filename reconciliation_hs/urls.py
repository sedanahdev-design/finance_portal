from django.urls import path

from reconciliation_hs import views

app_name = "reconciliation_hs"

urlpatterns = [
    path("", views.index, name="index"),
    path("run/", views.run_reconciliation, name="run"),
    path("result/<int:pk>/", views.result, name="result"),
    path("result/<int:pk>/download/", views.download, name="download"),
]
