from .models import SystemPage
from django.db.models import Q

def sidebar_permissions(request):
    """
    هذا المعالج السياقي يجهز قائمة الصفحات (الأيقونات) التي
    يجب أن تظهر في الشريط الجانبي للمستخدم الحالي بناءً على صلاحياته.
    """
    # نتأكد أولاً أن المستخدم قد سجل دخوله
    if not request.user.is_authenticated:
        return {}

    # المدير العام (Superuser) يرى كل الصفحات دائماً
    if request.user.is_superuser:
        # نقوم بتجميع الصفحات حسب الفئة (category)
        categories = {}
        all_pages = SystemPage.objects.all().order_by('category', 'name')
        for page in all_pages:
            if page.category not in categories:
                categories[page.category] = []
            categories[page.category].append(page)
        return {'sidebar_categories': categories}

    # بالنسبة للمستخدم العادي والموظفين
    # نحصل على المجموعات التي ينتمي إليها المستخدم
    user_groups = request.user.groups.all()
    
    # نحصل على الصلاحيات المباشرة الممنوحة للمستخدم
    user_permissions = request.user.user_permissions.all()
    # نحول الصلاحيات إلى قائمة من أسماء الأكواد (codenames) للصفحات
    permission_codenames = [p.codename for p in user_permissions]
    # نستخرج أسماء الصفحات من الـ codenames (مثال: 'view_systempage_المبيعات' -> 'المبيعات')
    allowed_page_names_from_perms = [name.replace('view_systempage_', '') for name in permission_codenames if name.startswith('view_systempage_')]


    # نقوم بجلب كل الصفحات التي تطابق صلاحيات المستخدم أو مجموعاته
    allowed_pages = SystemPage.objects.filter(
        Q(allowed_groups__in=user_groups) | Q(name__in=allowed_page_names_from_perms)
    ).distinct().order_by('category', 'name')

    # نقوم بتجميع الصفحات حسب الفئة (category) للعرض المنظم
    categories = {}
    for page in allowed_pages:
        if page.category not in categories:
            categories[page.category] = []
        categories[page.category].append(page)

    return {'sidebar_categories': categories}