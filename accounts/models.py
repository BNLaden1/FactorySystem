from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission  # <-- السطر المصحح
from django.conf import settings
import uuid

# ==================================
#   موديل صفحات النظام (للصلاحيات)
# ==================================


class SystemPage(models.Model):
    name = models.CharField(max_length=100, verbose_name="اسم الصفحة/الزر")
    url_name = models.CharField(
        max_length=100, unique=True, verbose_name="الاسم البرمجي للرابط")
    icon_name = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="اسم أيقونة Lucide")
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True,
                               blank=True, related_name='children', verbose_name="يتبع صفحة")
    allowed_groups = models.ManyToManyField(
        Group, blank=True, verbose_name="المجموعات المسموح لها بالوصول")

    def __str__(self):
        if self.parent:
            return f"{self.parent.name} -- {self.name}"
        return self.name

    class Meta:
        verbose_name = "صلاحية نظام"
        verbose_name_plural = "صلاحيات النظام"

# ==================================
#       موديل المستخدم المخصص
# ==================================


class User(AbstractUser):
    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        related_name="custom_user_set",
        related_query_name="user"
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        related_name="custom_user_permissions_set",
        related_query_name="user"
    )
    direct_permissions = models.ManyToManyField(
        SystemPage,
        blank=True,
        verbose_name="الصلاحيات المباشرة"
    )

    def __str__(self):
        return self.username

# ==================================
#       موديل الاشتراكات والتراخيص
# ==================================


class Subscription(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="المستخدم")
    serial_number = models.CharField(
        max_length=36, unique=True, editable=False, verbose_name="السيريال")
    start_date = models.DateField(
        null=True, blank=True, verbose_name="تاريخ بداية التفعيل")
    end_date = models.DateField(
        null=True, blank=True, verbose_name="تاريخ نهاية الاشتراك")
    is_active = models.BooleanField(
        default=False, verbose_name="الاشتراك فعال")

    class Meta:
        verbose_name = "اشتراك"
        verbose_name_plural = "الاشتراكات"

    def save(self, *args, **kwargs):
        if not self.serial_number:
            self.serial_number = str(uuid.uuid4())
        super().save(*args, **kwargs)

    def __str__(self):
        return f"اشتراك المستخدم: {self.user.username}"

    # ==================================
#   موديل ملف الشركة (للمعلومات الإضافية)
# ==================================


class CompanyProfile(models.Model):
    # كل ملف شركة مرتبط بمستخدم واحد فقط
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="company_profile")

    company_name = models.CharField(max_length=200, verbose_name="اسم الشركة")

    # سنستخدم CHOICES لتحديد الخيارات المتاحة
    CLASSIFICATION_CHOICES = [
        ('factory', 'مصنع'),
        ('store', 'متجر'),
        ('company', 'شركة خدمات'),
        ('other', 'أخرى'),
    ]
    classification = models.CharField(
        max_length=50, choices=CLASSIFICATION_CHOICES, verbose_name="تصنيف الشركة")

    country = models.CharField(max_length=100, verbose_name="الدولة")

    LANGUAGE_CHOICES = [
        ('ar', 'العربية'),
        ('en', 'الإنجليزية'),
    ]
    language = models.CharField(
        max_length=10, choices=LANGUAGE_CHOICES, default='ar', verbose_name="لغة النظام")

    # حقل للتأكد من أن المستخدم قد أكمل هذه البيانات
    has_completed_profile = models.BooleanField(default=False)

    def __str__(self):
        return self.company_name

    class Meta:
        verbose_name = "ملف شركة"
        verbose_name_plural = "ملفات الشركات"
