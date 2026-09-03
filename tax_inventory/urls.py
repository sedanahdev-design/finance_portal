from django.urls import path

from tax_inventory import views

app_name = "tax_inventory"

urlpatterns = [
    path("", views.index, name="index"),
    path("run/", views.run_view, name="run"),
    path("result/<int:pk>/", views.result, name="result"),
    path("result/<int:pk>/download/", views.download, name="download"),
]
