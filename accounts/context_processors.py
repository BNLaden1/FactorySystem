from .models import SystemPage

def sidebar_permissions(request):
    # إذا لم يكن المستخدم مسجل دخوله، لا نعرض له أي صلاحيات
    if not request.user.is_authenticated:
        return {}

    # (1) نحصل على الصلاحيات المباشرة المعطاة للمستخدم
    direct_pages = request.user.direct_permissions.all()

    # (2) نحصل على المجموعات التي ينتمي إليها المستخدم
    user_groups = request.user.groups.all()
    
    # (3) نحصل على الصلاحيات التي تأتي من خلال هذه المجموعات
    group_pages = SystemPage.objects.filter(allowed_groups__in=user_groups)
    
    # (4) ندمج كل الصلاحيات معاً (من مباشرة ومن المجموعات) ونزيل التكرار
    accessible_pages_all = (direct_pages | group_pages).filter(parent__isnull=True).distinct().order_by('id')

    # (5) نرسل القائمة النهائية للواجهة
    return {
        'accessible_pages': accessible_pages_all
    }