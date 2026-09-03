from django.utils.deprecation import MiddlewareMixin


class AuditLogMiddleware(MiddlewareMixin):
    """يلتقط عنوان IP الحالي بحيث يمكن لأي view تسجيله بسهولة عبر core.audit.log_action."""

    def process_request(self, request):
        request.client_ip = self._get_client_ip(request)
        return None

    @staticmethod
    def _get_client_ip(request):
        forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR")
