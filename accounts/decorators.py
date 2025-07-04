from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect

def page_permission_required(page_name):
    """
    Decorator للتأكد من أن المستخدم لديه صلاحية الوصول للصفحة.
    """
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            # المدير العام (Superuser) يمكنه الوصول لكل شيء
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)

            # تحقق إذا كان المستخدم لديه صلاحية مباشرة أو عبر مجموعة
            # هذا الكود يفترض وجود علاقة بين المستخدم وصفحاته المسموح بها
            # سنقوم ببناء هذا المنطق لاحقاً
            
            # حالياً، سنسمح بالمرور بشكل مؤقت
            # TODO: Implement actual permission logic here
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator