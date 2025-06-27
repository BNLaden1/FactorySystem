from django.core.management.base import BaseCommand
from accounts.models import SystemPage

# قائمة بكل الصفحات والأيقونات التي نريدها في الشريط الجانبي
PAGES = [
    {'name': 'الرئيسية', 'url_name': 'dashboard', 'icon_name': 'home'},
    {'name': 'المبيعات', 'url_name': 'sales_page', 'icon_name': 'shopping-cart'},
    {'name': 'العملاء', 'url_name': 'clients_page', 'icon_name': 'users'},
    {'name': 'عروض الأسعار', 'url_name': 'quotes_page', 'icon_name': 'file-text'},
    {'name': 'المناديب والمخازن', 'url_name': 'logistics_page', 'icon_name': 'truck'},
    {'name': 'المشتريات', 'url_name': 'purchases_page', 'icon_name': 'shopping-bag'},
    {'name': 'الأصناف', 'url_name': 'items_page', 'icon_name': 'package'},
    {'name': 'رفع ملف إكسل', 'url_name': 'upload_excel_page', 'icon_name': 'file-up'},
    {'name': 'مصروفات وإيرادات', 'url_name': 'transactions_page', 'icon_name': 'arrow-left-right'},
    {'name': 'الرسائل', 'url_name': 'messages_page', 'icon_name': 'message-square'},
    {'name': 'الموظفين والرواتب', 'url_name': 'hr_page', 'icon_name': 'users-round'},
    {'name': 'التقارير', 'url_name': 'reports_page', 'icon_name': 'bar-chart-3'},
    {'name': 'الخزن / نقاط البيع', 'url_name': 'pos_page', 'icon_name': 'landmark'},
    {'name': 'الإعدادات', 'url_name': 'settings_page', 'icon_name': 'settings'},
]

class Command(BaseCommand):
    help = 'Seeds the database with initial SystemPage data for the sidebar.'

    def handle(self, *args, **options):
        self.stdout.write('Seeding SystemPage data...')
        
        for page_data in PAGES:
            # هذا الأمر يبحث عن الصفحة، إذا لم يجدها يقوم بإنشائها
            # هذا يضمن أننا لن ننشئ صفحات مكررة إذا قمنا بتشغيل الأمر مرة أخرى
            page, created = SystemPage.objects.get_or_create(
                url_name=page_data['url_name'],
                defaults={
                    'name': page_data['name'],
                    'icon_name': page_data['icon_name'],
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Successfully created page: {page.name}'))
            else:
                self.stdout.write(f'Page already exists: {page.name}')

        self.stdout.write(self.style.SUCCESS('Seeding completed successfully!'))
        