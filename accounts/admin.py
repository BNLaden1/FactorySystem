from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Company, Subscription, CompanyProfile, SystemPage

# تخصيص عرض موديل المستخدم
class CustomUserAdmin(UserAdmin):
    # الحقول التي ستظهر في قائمة المستخدمين
    list_display = ('username', 'email', 'company', 'is_staff', 'is_active')
    # إضافة 'company' إلى الفلاتر
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups', 'company')
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('company',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('company',)}),
    )
    # تحديث filter_horizontal ليشير إلى الحقول الصحيحة
    filter_horizontal = ('groups', 'user_permissions')

# تخصيص عرض موديل الاشتراك
class SubscriptionAdmin(admin.ModelAdmin):
    # تم إضافة السيريال نمبر هنا
    list_display = ('company', 'serial_number', 'is_active', 'start_date', 'end_date', 'remaining_days')
    list_filter = ('is_active',)
    search_fields = ('company__name', 'serial_number')
    readonly_fields = ('serial_number', 'remaining_days')

# تخصيص عرض موديل ملف الشركة
class CompanyProfileAdmin(admin.ModelAdmin):
    list_display = ('company', 'country', 'classification', 'has_completed_profile')
    list_filter = ('classification', 'has_completed_profile')
    search_fields = ('company__name',)

# تخصيص عرض موديل الشركة
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)

# تخصيص عرض صفحات النظام
class SystemPageAdmin(admin.ModelAdmin):
    # إزالة الحقول غير الموجودة 'url_name' و 'parent'
    list_display = ('name', 'category', 'icon_class')
    list_filter = ('category',)
    search_fields = ('name', 'category')
    filter_horizontal = ('allowed_groups',)


# تسجيل المودلز مع التخصيصات الجديدة
admin.site.register(Company, CompanyAdmin)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(CompanyProfile, CompanyProfileAdmin)
admin.site.register(SystemPage, SystemPageAdmin)

from .models import ChartOfAccount
admin.site.register(ChartOfAccount)