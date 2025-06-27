from accounts.models import SystemPage

def sidebar_permissions(request):
    if not request.user.is_authenticated:
        return {}

    # جلب كل الصلاحيات الرئيسية (التي ليس لها أب)
    main_pages = SystemPage.objects.filter(parent__isnull=True).order_by('id')

    # فلترة الصفحات التي يملكها المستخدم مباشرة أو عبر المجموعات
    user_groups = request.user.groups.all()
    direct_pages = request.user.direct_permissions.filter(parent__isnull=True)
    group_pages = main_pages.filter(allowed_groups__in=user_groups)

    # دمج كل الصلاحيات بدون تكرار
    accessible_pages = (direct_pages | group_pages).distinct()

    return {
        'accessible_pages': accessible_pages
    }