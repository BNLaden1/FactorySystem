from django.core.management.base import BaseCommand
from accounts.models import Company, ChartOfAccount

class Command(BaseCommand):
    help = 'Seeds the database with a default chart of accounts for each company.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting to seed default Chart of Accounts...'))

        companies = Company.objects.all()

        for company in companies:
            self.stdout.write(f'Processing company: {company.name}')

            default_accounts = {
                'Asset': ['الخزنة', 'البنك', 'العملاء', 'عهد الموظفين'],
                'Liability': ['الموردين', 'قروض'],
                'Equity': ['رأس المال'],
                'Revenue': ['إيرادات المبيعات', 'إيرادات خدمات الورشة'],
                'Expense': ['مصروفات الأجور', 'مصروفات الإيجار', 'مصروفات الكهرباء', 'مصروفات متنوعة'],
            }
            
            for acc_type_en, sub_accounts in default_accounts.items():
                for acc_name in sub_accounts:
                    ChartOfAccount.objects.get_or_create(
                        company=company,
                        name=acc_name,
                        defaults={'account_type': acc_type_en}
                    )
            
            self.stdout.write(self.style.SUCCESS(f'Default accounts created for {company.name}'))

        self.stdout.write(self.style.SUCCESS('Account seeding completed successfully!'))