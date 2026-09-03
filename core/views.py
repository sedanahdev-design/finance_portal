from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy

from core.audit import log_action
from core.forms import ArabicLoginForm, ModuleAccessForm, StaffUserForm
from core.models import AuditLog, User
from core.module_registry import MODULES


class PortalLoginView(LoginView):
    template_name = "core/login.html"
    authentication_form = ArabicLoginForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        response = super().form_valid(form)
        log_action(self.request, AuditLog.Action.LOGIN, f"تسجيل دخول: {self.request.user}")
        return response


class PortalLogoutView(LogoutView):
    next_page = reverse_lazy("core:login")


@login_required
def dashboard(request):
    allowed_codes = request.user.accessible_module_codes()
    nav_modules = [m for m in MODULES if m.code in allowed_codes]
    recent_logs = AuditLog.objects.select_related("user")[:12] if request.user.is_supervisor else []
    return render(
        request,
        "core/dashboard.html",
        {"modules": nav_modules, "recent_logs": recent_logs},
    )


def _supervisor_only(request):
    return request.user.is_authenticated and request.user.is_supervisor


@login_required
def user_list(request):
    if not _supervisor_only(request):
        messages.error(request, "هذه الصفحة مخصّصة لمشرف القسم فقط.")
        return redirect("core:dashboard")
    users = User.objects.all().order_by("-date_joined")
    return render(request, "core/user_list.html", {"users": users})


@login_required
def user_edit(request, pk=None):
    if not _supervisor_only(request):
        messages.error(request, "هذه الصفحة مخصّصة لمشرف القسم فقط.")
        return redirect("core:dashboard")

    instance = get_object_or_404(User, pk=pk) if pk else None
    if request.method == "POST":
        form = StaffUserForm(request.POST, instance=instance)
        if form.is_valid():
            user = form.save()
            log_action(
                request, AuditLog.Action.ADMIN,
                f"{'تعديل' if instance else 'إنشاء'} مستخدم: {user.username}",
            )
            messages.success(request, "تم حفظ بيانات المستخدم بنجاح.")
            return redirect("core:user_access", pk=user.pk)
    else:
        form = StaffUserForm(instance=instance)
    return render(request, "core/user_form.html", {"form": form, "instance": instance})


@login_required
def user_access(request, pk):
    if not _supervisor_only(request):
        messages.error(request, "هذه الصفحة مخصّصة لمشرف القسم فقط.")
        return redirect("core:dashboard")

    target = get_object_or_404(User, pk=pk)
    if request.method == "POST":
        form = ModuleAccessForm(request.POST, user=target)
        if form.is_valid():
            form.save(granted_by=request.user)
            log_action(
                request, AuditLog.Action.ADMIN,
                f"تحديث صلاحيات الوحدات للمستخدم: {target.username}",
            )
            messages.success(request, "تم تحديث صلاحيات المستخدم.")
            return redirect("core:user_list")
    else:
        form = ModuleAccessForm(user=target)

    modules_with_fields = [
        {
            "module": m,
            "view": form[f"view_{m.code}"],
            "edit": form[f"edit_{m.code}"],
            "export": form[f"export_{m.code}"],
        }
        for m in MODULES
    ]
    return render(
        request,
        "core/user_access.html",
        {"form": form, "target": target, "modules_with_fields": modules_with_fields},
    )


@login_required
def audit_log_list(request):
    if not _supervisor_only(request):
        messages.error(request, "هذه الصفحة مخصّصة لمشرف القسم فقط.")
        return redirect("core:dashboard")
    logs = AuditLog.objects.select_related("user")[:300]
    return render(request, "core/audit_log_list.html", {"logs": logs})
