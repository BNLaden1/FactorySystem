from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from accounts.models import SystemPage

# ==============================================================================
#  القائمة النهائية والمنظمة لكل صفحات النظام
# ==============================================================================
PAGES = [
    # (هنا قائمة PAGES الكاملة التي اتفقنا عليها، لا تغيير عليها)
    # الفئة: رئيسية
    {'name': 'الرئيسية', 'url_name': 'dashboard', 'icon_class': 'layout-dashboard', 'category': 'رئيسية'},

    # الفئة: الإدارة
    {'name': 'إدارة الاشتراكات', 'url_name': 'manage_subscriptions', 'icon_class': 'gem', 'category': 'الإدارة'},
    {'name': 'إدارة المستخدمين', 'url_name': 'manage_users', 'icon_class': 'users', 'category': 'الإدارة'},
    {'name': 'إدارة الموظفين', 'url_name': 'manage_employees', 'icon_class': 'user-cog', 'category': 'الإدارة'},

    # الفئة: العمليات
    {'name': 'المشاريع', 'url_name': 'operations:project-list', 'icon_class': 'briefcase', 'category': 'العمليات'},
    {'name': 'أنواع التكاليف', 'url_name': 'operations:cost-type-manage', 'icon_class': 'tags', 'category': 'العمليات'},
    {'name': 'المبيعات', 'url_name': 'sales_page', 'icon_class': 'shopping-cart', 'category': 'العمليات'},
    {'name': 'فاتورة مبيعات', 'url_name': 'new_sale', 'category': 'العمليات', 'icon_class': 'receipt'},
    {'name': 'عروض الأسعار', 'url_name': 'quotes_page', 'icon_class': 'file-text', 'category': 'العمليات'},
    {'name': 'المشتريات', 'url_name': 'purchases_page', 'icon_class': 'shopping-bag', 'category': 'العمليات'},
    {'name': 'الأصناف', 'url_name': 'items_page', 'icon_class': 'package', 'category': 'العمليات'},

    # الفئة: المخازن
    {'name': 'المخزون', 'url_name': 'inventory_page', 'category': 'المخازن', 'icon_class': 'archive'},

    # الفئة: الحسابات
    {'name': 'إدارة العملاء', 'url_name': 'client_management', 'category': 'الحسابات', 'icon_class': 'contact'},
    {'name': 'دليل الحسابات', 'url_name': 'chart_of_accounts', 'category': 'الحسابات', 'icon_class': 'book-key'},
    {'name': 'قيود اليومية', 'url_name': 'journal_entry', 'category': 'الحسابات', 'icon_class': 'book-text'},
    {'name': 'إدارة الخزن', 'url_name': 'cashbox_management', 'category': 'الحسابات', 'icon_class': 'wallet'},
    {'name': 'تسجيل حركة خزنة', 'url_name': 'new_cashbox_transaction', 'category': 'الحسابات', 'icon_class': 'receipt'},
    {'name': 'تقرير حركة خزنة', 'url_name': 'cashbox_report', 'category': 'الحسابات', 'icon_class': 'book-copy'},

    # الفئة: التحليلات
    {'name': 'التقارير', 'url_name': 'reports_page', 'icon_class': 'bar-chart-3', 'category': 'التحليلات'},

    # الفئة: النظام
    {'name': 'الإعدادات', 'url_name': 'settings_dashboard', 'category': 'النظام', 'icon_class': 'settings'},
]
# ==============================================================================

class Command(BaseCommand):
    help = 'Clears and seeds pages, and assigns all permissions to the main manager group.'

    def handle(self, *args, **options):
        # ... (الجزء الخاص بحذف وإنشاء الصفحات يبقى كما هو) ...
        self.stdout.write(self.style.WARNING('Clearing all existing SystemPage data...'))
        SystemPage.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('✔ All old pages have been deleted.'))
        self.stdout.write('---------------------------------')
        self.stdout.write(self.style.SUCCESS('Starting to seed new SystemPage data...'))

        for page_data in PAGES:
            SystemPage.objects.create(
                name=page_data['name'],
                url_name=page_data['url_name'],
                icon_class=page_data['icon_class'],
                category=page_data['category'],
            )
        self.stdout.write(self.style.SUCCESS('✔ Page seeding completed successfully!'))
        self.stdout.write('---------------------------------')

        # ▼▼▼ هذا هو الجزء الجديد والمهم الذي يمنح الصلاحيات ▼▼▼
        self.stdout.write(self.style.SUCCESS('Assigning all page permissions to the main manager group...'))
        try:
            # 1. نحضر أو ننشئ مجموعة "مدراء الشركات"
            manager_group, created = Group.objects.get_or_create(name='مدراء الشركات')
            if created:
                self.stdout.write(self.style.SUCCESS('  Created new group: مدراء الشركات'))

            # 2. نحضر كل صفحات النظام
            all_pages = SystemPage.objects.all()

            # 3. نمنح المجموعة كل الصلاحيات (سيقوم بمسح القديم وإضافة الجديد)
            manager_group.system_pages.set(all_pages)

            self.stdout.write(self.style.SUCCESS(f'✔ Successfully assigned {all_pages.count()} permissions to the group.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Could not assign permissions: {e}'))

        self.stdout.write('---------------------------------')
        self.stdout.write(self.style.SUCCESS('All tasks completed!'))