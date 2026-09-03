from core.module_registry import MODULES


def modules_nav(request):
    """يوفر لكل القوالب قائمة الوحدات المسموح للمستخدم الحالي بالوصول إليها، لبناء القائمة الجانبية."""
    if not getattr(request, "user", None) or not request.user.is_authenticated:
        return {}

    allowed_codes = request.user.accessible_module_codes()
    nav_modules = [m for m in MODULES if m.code in allowed_codes]
    return {
        "nav_modules": nav_modules,
        "is_supervisor": request.user.is_supervisor,
    }
