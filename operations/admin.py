# operations/admin.py
from django.contrib import admin
# ▼▼▼ نستدعي النماذج الجديدة والصحيحة من ملف models.py ▼▼▼
from .models import Project, CostItem, Payment

# هذا الكود يسمح لنا بإضافة بنود التكلفة والدفعات من داخل صفحة المشروع مباشرة
class CostItemInline(admin.TabularInline):
    model = CostItem
    extra = 1 # عدد الصفوف الفارغة الجديدة

class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 1 # عدد الصفوف الفارغة الجديدة

# هذا الكود الرئيسي لتسجيل المشروع في لوحة التحكم
class ProjectAdmin(admin.ModelAdmin):
    inlines = [CostItemInline, PaymentInline] # نضع الجداول المضمنة هنا
    list_display = ('name', 'client', 'status', 'total_costs', 'total_payments', 'remaining_balance')
    list_filter = ('status', 'client')
    search_fields = ('name', 'client__name')

# نسجل النماذج في لوحة التحكم
admin.site.register(Project, ProjectAdmin)
# يمكنك إلغاء تسجيل النموذجين التاليين إذا أردت إضافتهما فقط من خلال المشروع
admin.site.register(CostItem)
admin.site.register(Payment)