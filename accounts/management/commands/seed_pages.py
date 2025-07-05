from django.core.management.base import BaseCommand
from accounts.models import SystemPage

# ==============================================================================
#  القائمة النهائية والمنظمة لكل صفحات النظام
# ==============================================================================
PAGES = [
    # الفئة: رئيسية
    {'name': 'الرئيسية', 'url_name': 'dashboard', 'icon_class': 'layout-dashboard', 'category': 'رئيسية'},

    # الفئة: الإدارة
    {'name': 'إدارة الاشتراكات', 'url_name': 'manage_subscriptions', 'icon_class': 'gem', 'category': 'الإدارة'},
    {'name': 'إدارة المستخدمين', 'url_name': 'manage_users', 'icon_class': 'users', 'category': 'الإدارة'},

    # الفئة: العمليات
    {'name': 'المبيعات', 'url_name': 'sales_page', 'icon_class': 'shopping-cart', 'category': 'العمليات'},
    {'name': 'فاتورة مبيعات', 'url_name': 'new_sale', 'category': 'العمليات', 'icon_class': 'receipt'},
    {'name': 'عروض الأسعار', 'url_name': 'quotes_page', 'icon_class': 'file-text', 'category': 'العمليات'},
    {'name': 'المشتريات', 'url_name': 'purchases_page', 'icon_class': 'shopping-bag', 'category': 'العمليات'},
    {'name': 'الأصناف', 'url_name': 'items_page', 'icon_class': 'package', 'category': 'العمليات'},

    # الفئة: المخازن
    {'name': 'المخزون', 'url_name': 'inventory_page', 'category': 'المخازن', 'icon_class': 'archive'},

    # الفئة: الحسابات
    {'name': 'دليل الحسابات', 'url_name': 'chart_of_accounts', 'category': 'الحسابات', 'icon_class': 'book-key'},
    {'name': 'قيود اليومية', 'url_name': 'journal_entry', 'category': 'الحسابات', 'icon_class': 'book-text'},
    {'name': 'إدارة الخزن', 'url_name': 'cashbox_management', 'category': 'الحسابات', 'icon_class': 'wallet'},
    {'name': 'تسجيل حركة خزنة', 'url_name': 'new_cashbox_transaction', 'category': 'الحسابات', 'icon_class': 'receipt'},
    {'name': 'تقرير حركة خزنة', 'url_name': 'cashbox_report', 'category': 'الحسابات', 'icon_class': 'book-copy'},

    # الفئة: الموارد البشرية
    {'name': 'الموظفين والرواتب', 'url_name': 'hr_page', 'icon_class': 'user-cog', 'category': 'الموارد البشرية'},
    
    # الفئة: التحليلات
    {'name': 'التقارير', 'url_name': 'reports_page', 'icon_class': 'bar-chart-3', 'category': 'التحليلات'},

    # الفئة: النظام
    {'name': 'الإعدادات', 'url_name': 'settings_dashboard', 'category': 'النظام', 'icon_class': 'settings'},
]
# ==============================================================================

class Command(BaseCommand):
    help = 'Clears and seeds the database with fresh SystemPage data for the sidebar.'

    def handle(self, *args, **options):
        # الخطوة 1: حذف كل الصفحات القديمة لضمان عدم وجود بيانات خاطئة
        self.stdout.write(self.style.WARNING('Clearing all existing SystemPage data...'))
        SystemPage.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('✔ All old pages have been deleted.'))
        self.stdout.write('---------------------------------')

        # الخطوة 2: إضافة الصفحات الجديدة والنظيفة من القائمة المحدثة
        self.stdout.write(self.style.SUCCESS('Starting to seed new SystemPage data...'))
        
        for page_data in PAGES:
            SystemPage.objects.create(
                name=page_data['name'],
                url_name=page_data['url_name'],
                icon_class=page_data['icon_class'],
                category=page_data['category'],
            )
            self.stdout.write(self.style.SUCCESS(f"  Successfully created page: {page_data['name']}"))

        self.stdout.write('---------------------------------')
        self.stdout.write(self.style.SUCCESS('✔ Seeding completed successfully!'))