from django.shortcuts import redirect
from django.urls import reverse, resolve
from django.urls.exceptions import Resolver404

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # (1) الآن نسجل فقط "أسماء" الصفحات المسموح بها
        self.allowed_url_names = ['login', 'register', 'logout', 'activate_account']

    def __call__(self, request):
        # نستثني لوحة تحكم الأدمن من هذه الحماية
        if request.path.startswith(reverse('admin:index')):
            return self.get_response(request)

        # إذا كان المستخدم مسجل دخوله بالفعل، اسمح له بالمرور لأي مكان
        if request.user.is_authenticated:
            return self.get_response(request)

        # (2) إذا كان المستخدم زائراً، نبدأ في التحقق
        try:
            # نحاول معرفة "اسم" الرابط الذي يحاول الزائر الوصول إليه
            current_url_name = resolve(request.path_info).url_name
            # إذا كان اسم الرابط موجوداً في قائمة الأسماء المسموح بها، اسمح له بالمرور
            if current_url_name in self.allowed_url_names:
                return self.get_response(request)
        except Resolver404:
            # إذا كان الرابط غير موجود أصلاً، دعه يكمل ليظهر خطأ 404
            return self.get_response(request)

        # (3) إذا وصل الكود إلى هنا، فهذا يعني أن المستخدم زائر ويحاول الوصول لصفحة محمية
        # نقوم بتحويله إلى صفحة تسجيل الدخول
        return redirect('login')