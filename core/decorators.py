from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


def module_required(module_code, edit=False):
    """
    ديكوريتر يمنع الوصول لأي صفحة من صفحات وحدة معينة إن لم يملك المستخدم
    صلاحية عرضها (أو تعديلها إن edit=True). يُستخدم على كل views.py في
    تطبيقات الحلول التسعة، بحيث تكون الصلاحيات قابلة للضبط من قبل المشرف
    دون الحاجة لتعديل الكود.
    """

    def decorator(view_func):
        @login_required(login_url="core:login")
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            allowed = (
                request.user.can_edit(module_code)
                if edit
                else request.user.can_access(module_code)
            )
            if not allowed:
                messages.error(request, "لا تملك صلاحية الوصول إلى هذه الوحدة.")
                return redirect("core:dashboard")
            return view_func(request, *args, **kwargs)

        return _wrapped

    return decorator
