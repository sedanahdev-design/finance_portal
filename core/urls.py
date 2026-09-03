from django.urls import path

from core import views

app_name = "core"

urlpatterns = [
    path("login/", views.PortalLoginView.as_view(), name="login"),
    path("logout/", views.PortalLogoutView.as_view(), name="logout"),
    path("", views.dashboard, name="dashboard"),
    path("users/", views.user_list, name="user_list"),
    path("users/new/", views.user_edit, name="user_new"),
    path("users/<int:pk>/edit/", views.user_edit, name="user_edit"),
    path("users/<int:pk>/access/", views.user_access, name="user_access"),
    path("audit-log/", views.audit_log_list, name="audit_log"),
]
