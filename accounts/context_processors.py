from accounts.models import SystemPage

def sidebar_permissions(request):
    """
    هذا المعالج يجعل قائمة الصفحات المتاحة للمستخدم
    متوفرة في كل قوالب المشروع.
    """
    # إذا لم يكن المستخدم مسجل دخوله، لا نعرض له أي صلاحيات
    if not request.user.is_authenticated:
        return {}

    accessible_pages = []
    
    # نحصل على كل الصلاحيات الرئيسية (التي ليس لها أب)
    main_pages = SystemPage.objects.filter(parent__isnull=True).order_by('id')
    
    for page in main_pages:
        # نتحقق من الصلاحيات المباشرة للمستخدم
        has_direct_permission = request.user.direct_permissions.filter(id=page.id).exists()
        
        # نتحقق من الصلاحيات الموروثة من المجموعات
        has_group_permission = page.allowed_groups.filter(id__in=request.user.groups.all()).exists()

        # إذا كان يملك أي نوع من الصلاحية، نعرض له الصفحة
        if has_direct_permission or has_group_permission or request.user.is_superuser:
            accessible_pages.append(page)

    return {
        'accessible_pages': accessible_pages
    }