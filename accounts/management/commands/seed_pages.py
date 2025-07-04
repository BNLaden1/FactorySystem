from django.core.management.base import BaseCommand
from accounts.models import SystemPage, Group
from django.utils.translation import gettext_lazy as _

# قائمة بكل الصفحات والأيقونات التي نريدها في الشريط الجانبي
# تم تحديثها لتتوافق مع الموديل الجديد
PAGES = [
    # الفئة: رئيسية
    {'name': 'الرئيسية', 'url_name': 'dashboard', 'icon_class': 'layout-dashboard', 'category': 'رئيسية'},
    
    # الفئة: الإدارة
    {'name': 'إدارة الاشتراكات', 'url_name': 'manage_subscriptions', 'icon_class': 'gem', 'category': 'الإدارة'},
    {'name': 'إدارة المستخدمين', 'url_name': 'manage_users', 'icon_class': 'users', 'category': 'الإدارة'},

    # الفئة: الصفحات العامة
    {'name': 'المبيعات', 'url_name': 'sales_page', 'icon_class': 'shopping-cart', 'category': 'العمليات'},
    {'name': 'العملاء', 'url_name': 'clients_page', 'icon_class': 'contact', 'category': 'العمليات'},
    {'name': 'عروض الأسعار', 'url_name': 'quotes_page', 'icon_class': 'file-text', 'category': 'العمليات'},
    {'name': 'المشتريات', 'url_name': 'purchases_page', 'icon_class': 'shopping-bag', 'category': 'العمليات'},
    {'name': 'الأصناف', 'url_name': 'items_page', 'icon_class': 'package', 'category': 'العمليات'},
    # ▼▼▼ أضف هذا السطر الجديد ▼▼▼
    {'name': 'المخزون', 'url_name': 'inventory_page', 'category': 'المخازن', 'icon_class': 'archive'},
    {'name': 'الموظفين والرواتب', 'url_name': 'hr_page', 'icon_class': 'user-cog', 'category': 'الموارد البشرية'},
    {'name': 'التقارير', 'url_name': 'reports_page', 'icon_class': 'bar-chart-3', 'category': 'التحليلات'},
    {'name': 'الإعدادات', 'url_name': 'settings_page', 'icon_class': 'settings', 'category': 'النظام'},
        {'name': 'الأصناف', 'url_name': 'items_page', 'icon_class': 'package', 'category': 'العمليات'},

    # ▼▼▼ هذا هو السطر الذي يجب إضافته ▼▼▼

    {'name': 'الموظفين والرواتب', 'url_name': 'hr_page', 'icon_class': 'user-cog', 'category': 'الموارد البشرية'},
    {'name': 'فاتورة مبيعات', 'url_name': 'new_sale', 'category': 'العمليات', 'icon_class': 'receipt'},

    #شجرة الحسابات
    {'name': 'قيود اليومية', 'url_name': 'journal_entry', 'category': 'الحسابات', 'icon_class': 'book-text'},
    {'name': 'دليل الحسابات', 'url_name': 'chart_of_accounts', 'category': 'الحسابات', 'icon_class': 'book-key'},
]

class Command(BaseCommand):
    help = 'Seeds the database with initial SystemPage data for the sidebar.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting to seed SystemPage data...'))
        
        # يمكننا إنشاء مجموعة "مدراء النظام" هنا إذا لم تكن موجودة
        # admin_group, created = Group.objects.get_or_create(name='مدراء النظام')
        
        for page_data in PAGES:
            page, created = SystemPage.objects.get_or_create(
                url_name=page_data['url_name'],
                defaults={
                    'name': page_data['name'],
                    'icon_class': page_data['icon_class'],
                    'category': page_data['category'],
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Successfully created page: {page.name}"))
                # يمكنك إضافة صلاحيات للمجموعات هنا إذا أردت
                # if page_data['category'] == 'الإدارة':
                #     page.allowed_groups.add(admin_group)
            else:
                self.stdout.write(f'Page "{page.name}" already exists.')

        self.stdout.write(self.style.SUCCESS('Seeding completed successfully!'))

        