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