from core.models import AuditLog


def log_action(request, action, message, module_code="", meta=None):
    """تسجيل عملية في سجل التدقيق. يُستخدم من كل تطبيقات الحلول التسعة."""
    AuditLog.objects.create(
        user=request.user if request.user.is_authenticated else None,
        module_code=module_code,
        action=action,
        message=message,
        meta=meta or {},
        ip_address=getattr(request, "client_ip", None),
    )
