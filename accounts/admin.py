from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Subscription, SystemPage

# --- واجهة مخصصة لموديل User ---
class CustomUserAdmin(UserAdmin):
    # هذا يخص موديل User فقط ويحسن شكل اختيار الصلاحيات
    filter_horizontal = ('groups', 'user_permissions', 'direct_permissions')
    
    # هذا يضيف قسم "الصلاحيات المباشرة" في صفحة تعديل المستخدم
    fieldsets = UserAdmin.fieldsets + (
        ("صلاحيات مخصصة", {'fields': ('direct_permissions',)}),
    )
    list_display = ('username', 'email', 'is_active', 'is_staff')
    list_filter = ('is_active', 'is_staff', 'groups')

# --- واجهة مخصصة لموديل SystemPage ---
class SystemPageAdmin(admin.ModelAdmin):
    # هنا نعرض فقط الحقول التي تنتمي لموديل SystemPage
    filter_horizontal = ('allowed_groups',)
    list_display = ('__str__', 'url_name')
    list_filter = ('parent',)
    search_fields = ('name',)

# --- واجهة مخصصة لموديل Subscription ---
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'serial_number', 'end_date', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('user__username',)

# --- التسجيل النهائي ---
# نتأكد من أننا نسجل كل موديل مع الواجهة الصحيحة الخاصة به
admin.site.register(User, CustomUserAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(SystemPage, SystemPageAdmin)