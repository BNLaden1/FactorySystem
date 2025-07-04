from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils.translation import gettext_lazy as _
import uuid
from datetime import timedelta
from django.utils import timezone

class Company(models.Model):
    name = models.CharField(max_length=255, verbose_name="اسم الشركة")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    class Meta:
        verbose_name = "شركة"
        verbose_name_plural = "1. الشركات"
    def __str__(self): return self.name

class User(AbstractUser):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True, verbose_name="الشركة")
    class Meta:
        verbose_name = "مستخدم"
        verbose_name_plural = "5. المستخدمون"

class Subscription(models.Model):
    company = models.OneToOneField(Company, on_delete=models.CASCADE, verbose_name="الشركة")
    serial_number = models.CharField(max_length=100, unique=True, default=uuid.uuid4, editable=False, verbose_name="السيريال نمبر")
    is_active = models.BooleanField(default=False, verbose_name="فعّال")
    start_date = models.DateField(null=True, blank=True, verbose_name="تاريخ البداية")
    end_date = models.DateField(null=True, blank=True, verbose_name="تاريخ النهاية")
    class Meta:
        verbose_name = "اشتراك"
        verbose_name_plural = "3. الاشتراكات"
    def __str__(self): return f"اشتراك شركة: {self.company.name}"
    def activate(self):
        self.is_active = True
        self.start_date = timezone.now().date()
        self.end_date = self.start_date + timedelta(days=365)
        self.save()
    @property
    def remaining_days(self):
        if self.is_active and self.end_date:
            return max(0, (self.end_date - timezone.now().date()).days)
        return 0

class CompanyProfile(models.Model):
    company = models.OneToOneField(Company, on_delete=models.CASCADE, verbose_name="الشركة")
    CLASSIFICATION_CHOICES = [('factory', 'مصنع'), ('store', 'متجر'), ('company', 'شركة خدمات')]
    country = models.CharField(max_length=100, blank=True, null=True, verbose_name="الدولة")
    classification = models.CharField(max_length=50, choices=CLASSIFICATION_CHOICES, blank=True, null=True, verbose_name="تصنيف الشركة")
    language = models.CharField(max_length=10, default='ar', verbose_name="اللغة")
    has_completed_profile = models.BooleanField(default=False, verbose_name="أكمل ملفه")
    class Meta:
        verbose_name = "ملف شركة"
        verbose_name_plural = "2. ملفات الشركات"
    def __str__(self): return f"ملف شركة: {self.company.name}"

class SystemPage(models.Model):
    name = models.CharField(max_length=100, verbose_name="اسم الصفحة المعروض")
    # هذا هو الحقل الذي سبب المشكلة، يجب أن يكون موجوداً هنا
    url_name = models.CharField(max_length=100, unique=True, verbose_name="اسم الرابط (من urls.py)")
    icon_class = models.CharField(max_length=50, blank=True, null=True, verbose_name="أيقونة Lucide")
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children', verbose_name="يتبع صفحة")
    allowed_groups = models.ManyToManyField(Group, blank=True, verbose_name="المجموعات المسموح لها بالوصول",
    related_name="system_pages")
    category = models.CharField(max_length=100, default='General', verbose_name="الفئة")
    
    def __str__(self):
        if self.parent:
            return f"{self.parent.name} -> {self.name}"
        return self.name
    class Meta:
        verbose_name = "صفحة نظام"
        verbose_name_plural = "4. صفحات النظام"
        ordering = ['parent__id', 'id']
        # في نهاية ملف accounts/models.py

class IPRegistrationRecord(models.Model):
    ip_address = models.GenericIPAddressField(unique=True, verbose_name="عنوان IP")
    company = models.OneToOneField(Company, on_delete=models.CASCADE, verbose_name="الشركة المسجلة")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="وقت التسجيل")

    def __str__(self):
        return f"{self.ip_address} - {self.company.name}"

    class Meta:
        verbose_name = "سجل تسجيل IP"
        verbose_name_plural = "سجلات تسجيل IP"

        # =============================================
#           الموديل الجديد: الأصناف
# =============================================
class Item(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name="الشركة")
    name = models.CharField(max_length=200, verbose_name="اسم الصنف")
    code = models.CharField(max_length=50, blank=True, null=True, verbose_name="كود الصنف")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="سعر البيع")
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="سعر التكلفة")
    quantity = models.PositiveIntegerField(default=0, verbose_name="الكمية الحالية")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإضافة")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "صنف"
        verbose_name_plural = "6. الأصناف"

        # accounts/models.py

# ... (كل النماذج الموجودة بالفعل مثل Company, User, Item تبقى كما هي) ...


# ▼▼▼ بداية الكود الجديد للنماذج المحاسبية ▼▼▼

class ChartOfAccount(models.Model):
    """
    نموذج دليل الحسابات (شجرة الحسابات).
    يحتوي على كل الحسابات الممكنة في النظام.
    """
    ACCOUNT_TYPE_CHOICES = [
        ('Asset', 'أصل'),
        ('Liability', 'التزام'),
        ('Equity', 'حقوق ملكية'),
        ('Revenue', 'إيراد'),
        ('Expense', 'مصروف'),
    ]

    name = models.CharField(max_length=100, verbose_name="اسم الحساب")
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPE_CHOICES, verbose_name="نوع الحساب")
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='children', verbose_name="الحساب الأب")
    
    # كل حساب يتبع لشركة معينة لضمان العزل
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='chart_of_accounts', verbose_name="الشركة")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "حساب في الدليل"
        verbose_name_plural = "دليل الحسابات"


class JournalEntry(models.Model):
    """
    نموذج قيد اليومية. يمثل كل معاملة مالية.
    """
    date = models.DateField(auto_now_add=True, verbose_name="تاريخ القيد")
    description = models.CharField(max_length=255, verbose_name="البيان/الوصف")
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='journal_entries', verbose_name="الشركة")

    def __str__(self):
        return f"قيد رقم {self.id} - {self.description}"

    class Meta:
        verbose_name = "قيد يومية"
        verbose_name_plural = "قيود اليومية"


class Transaction(models.Model):
    """
    نموذج الحركة المالية. يمثل كل سطر (مدين أو دائن) في قيد اليومية.
    """
    # ✨ 1. هذه هي القائمة التي كانت مفقودة أو غير صحيحة ✨
    TRANSACTION_TYPE_CHOICES = [
        ('General', 'عام'),
        ('Sarf', 'سند صرف'),
        ('Qabd', 'سند قبض'),
        ('Taswya', 'تسوية عهدة'),
        ('Ajel', 'آجل'),
    ]

    journal_entry = models.ForeignKey(JournalEntry, on_delete=models.CASCADE, related_name='transactions', verbose_name="القيد الأصلي")
    account = models.ForeignKey(ChartOfAccount, on_delete=models.PROTECT, verbose_name="الحساب")
    debit = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="مدين (صدر له)")
    credit = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="دائن (صدر منه)")
    
    # ✨ 2. وهذا هو الحقل الذي يستخدم القائمة ✨
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES, default='General', verbose_name="نوع الحركة")

    def __str__(self):
        return f"حركة على حساب {self.account.name}"

    class Meta:
        verbose_name = "حركة مالية"
        verbose_name_plural = "الحركات المالية"

        # ▼▼▼ بداية الكود الجديد لموديول الخزنة ▼▼▼

class Cashbox(models.Model):
    """
    يمثل كل خزنة في الشركة (نقدية، بنك، عهدة).
    """
    CASHBOX_TYPE_CHOICES = [
        ('cash', 'نقدية'),
        ('bank', 'بنكية'),
        ('custody', 'عهدة'),
    ]

    name = models.CharField(max_length=100, verbose_name="اسم الخزنة/الحساب")
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="الرصيد الحالي")
    box_type = models.CharField(max_length=20, choices=CASHBOX_TYPE_CHOICES, default='cash', verbose_name="نوع الخزنة")
    is_active = models.BooleanField(default=True, verbose_name="مفعّلة")
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='cashboxes', verbose_name="الشركة")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "خزنة"
        verbose_name_plural = "الخزن"


class CashboxTransaction(models.Model):
    """
    يمثل كل حركة مالية (صرف أو تحصيل) من خزنة معينة.
    """
    TRANSACTION_TYPE_CHOICES = [
        ('in', 'تحصيل/إيداع'),
        ('out', 'صرف/سحب'),
    ]
    CATEGORY_CHOICES = [
        ('salary', 'راتب'),
        ('expense', 'مصروف'),
        ('supplier_payment', 'دفعة لمورد'),
        ('customer_payment', 'تحصيل من عميل'),
        ('custody_settlement', 'تسوية عهدة'),
        ('other', 'أخرى'),
    ]

    cashbox = models.ForeignKey(Cashbox, on_delete=models.PROTECT, related_name='transactions', verbose_name="الخزنة")
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE_CHOICES, verbose_name="نوع العملية")
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="المبلغ")
    date = models.DateTimeField(default=timezone.now, verbose_name="التاريخ")
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, verbose_name="التصنيف")
    description = models.TextField(verbose_name="البيان/الوصف")
    
    # يمكنك إضافة حقول لربط الحركة بالموظف/العميل/المورد لاحقًا
    # related_employee = models.ForeignKey(User, ...)
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='cashbox_transactions')

    def __str__(self):
        return f"{self.get_transaction_type_display()} من/إلى {self.cashbox.name} بقيمة {self.amount}"

    class Meta:
        verbose_name = "حركة خزنة"
        verbose_name_plural = "حركات الخزن"
        ordering = ['-date']
        
# ▲▲▲ نهاية الكود الجديد ▲▲▲