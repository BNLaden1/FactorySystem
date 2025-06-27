from accounts.models import SystemPage

def sidebar_permissions(request):
    # ننشئ قاموساً فارغاً للبدء
    context = {
        'accessible_pages': []
    }

    # نتأكد من أن المستخدم مسجل دخوله، وإلا لن يحصل على أي صلاحيات
    if request.user.is_authenticated:
        
        # الحالة الأولى: إذا كان المستخدم سوبر يوزر، أعطه كل الصلاحيات الرئيسية
        if request.user.is_superuser:
            accessible_pages = SystemPage.objects.filter(parent__isnull=True).order_by('id')
        else:
            # إذا كان مستخدماً عادياً
            user_groups = request.user.groups.all()
            
            # الصلاحيات المباشرة المعطاة للمستخدم
            direct_pages = request.user.direct_permissions.filter(parent__isnull=True)
            
            # الصلاحيات الموروثة من المجموعات
            group_pages = SystemPage.objects.filter(allowed_groups__in=user_groups, parent__isnull=True)
            
            # ندمج كل الصلاحيات بدون تكرار
            accessible_pages = (direct_pages | group_pages).distinct().order_by('id')
        
        # نقوم بطباعة النتيجة في الـ Terminal لنتأكد منها
        print(f"--- DEBUG: User '{request.user.username}' has access to: {list(accessible_pages)} ---")

        # نضع القائمة النهائية في الـ context
        context['accessible_pages'] = accessible_pages

    return context