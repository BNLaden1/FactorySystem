from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Company

# نستخدم get_user_model للحصول على نموذج المستخدم الذي يستخدمه جانغو
User = get_user_model()

# كل كلاس اختبار يجب أن يرث من TestCase
class CompanyModelTest(TestCase):

    # هذه الدالة يتم استدعاؤها تلقائيًا قبل كل اختبار
    def setUp(self):
        """
        نقوم هنا بإعداد البيانات التي سنحتاجها للاختبار.
        """
        # سنقوم بإنشاء شركة افتراضية لاختبارها
        Company.objects.create(name="Test Company")

    def test_company_creation(self):
        """
        الاختبار الأول: نتأكد من أن الشركة تم إنشاؤها بنجاح.
        """
        # 1. نجلب الشركة التي أنشأناها من قاعدة البيانات
        company = Company.objects.get(name="Test Company")
        
        # 2. نستخدم self.assertEqual لنتأكد من أن اسمها صحيح
        # هذا السطر يقول: "هل اسم الشركة التي جلبتها يساوي 'Test Company'؟"
        self.assertEqual(company.name, "Test Company")
        
        # 3. نطبع رسالة نجاح في التيرمينال (اختياري)
        print("SUCCESS: test_company_creation - Company was created successfully.")