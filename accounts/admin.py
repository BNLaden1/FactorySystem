from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Subscription, SystemPage

# --- واجهة مخصصة لموديل User ---
class CustomUserAdmin(UserAdmin):
    filter_horizontal = ('groups', 'user_permissions', 'direct_permissions')
    fieldsets = UserAdmin.fieldsets + (
        ("صلاحيات مخصصة", {'fields': ('direct_permissions',)}),
    )
    list_display = ('username', 'email', 'is_active', 'is_staff')
    list_filter = ('is_active', 'is_staff', 'groups')

# --- (!!!) واجهة صلاحيات النظام المحدثة والاحترافية (التي أرسلتها أنت) (!!!) ---
class SystemPageAdmin(admin.ModelAdmin):
    # هذا الحقل هو الذي يجعل اختيار المجموعات سهلاً
    filter_horizontal = ('allowed_groups',)

    # هذا الحقل سيقسم الصفحة وينظمها ويضيف نصاً توضيحياً
    fieldsets = (
        (None, {
            'fields': ('name', 'url_name', 'icon_name', 'parent')
        }),
        ('الصلاحيات', {
            'fields': ('allowed_groups',),
            'description': 'اختر المجموعات التي يمكنها رؤية هذه الصفحة أو الأيقونة. سيتم تطبيق الصلاحية على كل المستخدمين داخل المجموعة المختارة.'
        }),
    )
    list_display = ('__str__', 'url_name')
    list_filter = ('parent',)
    search_fields = ('name',)

# --- واجهة مخصصة لموديل Subscription ---
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'serial_number', 'end_date', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('user__username',)

# --- التسجيل النهائي ---
admin.site.register(User, CustomUserAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(SystemPage, SystemPageAdmin)