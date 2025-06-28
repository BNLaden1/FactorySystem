from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils.translation import gettext_lazy as _
import uuid
from datetime import timedelta
from django.utils import timezone

# الخطوة 1: إنشاء موديل الشركة
class Company(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("Company Name"))
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Company")
        verbose_name_plural = _("Companies")


# الخطوة 2: تعديل موديل المستخدم وربطه بالشركة
class User(AbstractUser):
    # ربط المستخدم بالشركة. كل مستخدم يجب أن يكون تابعاً لشركة.
    company = models.ForeignKey(
        Company, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        verbose_name=_("Company")
    )
    
    groups = models.ManyToManyField(
        Group,
        verbose_name=_('groups'),
        blank=True,
        help_text=_(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        related_name="custom_user_set",  # اسم related_name جديد
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('user permissions'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name="custom_user_set_permissions", # اسم related_name جديد
        related_query_name="user",
    )

    def __str__(self):
        return self.username


# الخطوة 3: تعديل موديل الاشتراك وربطه بالشركة
class Subscription(models.Model):
    # ربط الاشتراك بالشركة مباشرة
    company = models.OneToOneField(
        Company, 
        on_delete=models.CASCADE, 
        verbose_name=_("Company")
    )
    serial_number = models.CharField(
        max_length=100, 
        unique=True, 
        default=uuid.uuid4, 
        editable=False
    )
    is_active = models.BooleanField(default=False, verbose_name=_("Is Active"))
    start_date = models.DateField(null=True, blank=True, verbose_name=_("Start Date"))
    end_date = models.DateField(null=True, blank=True, verbose_name=_("End Date"))

    def __str__(self):
        return f"Subscription for {self.company.name}"

    def activate(self):
        self.is_active = True
        self.start_date = timezone.now().date()
        self.end_date = self.start_date + timedelta(days=365)
        self.save()

    @property
    def remaining_days(self):
        if self.is_active and self.end_date:
            remaining = self.end_date - timezone.now().date()
            return max(0, remaining.days)
        return 0

    class Meta:
        verbose_name = _("Subscription")
        verbose_name_plural = _("Subscriptions")


# الخطوة 4: تعديل ملف الشركة وربطه بالشركة
class CompanyProfile(models.Model):
    # ربط البروفايل بالشركة
    company = models.OneToOneField(
        Company, 
        on_delete=models.CASCADE, 
        verbose_name=_("Company")
    )
    
    CLASSIFICATION_CHOICES = [
        ('factory', _('Factory')),
        ('store', _('Store')),
        ('company', _('Company')),
    ]
    country = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("Country"))
    classification = models.CharField(max_length=50, choices=CLASSIFICATION_CHOICES, blank=True, null=True, verbose_name=_("Classification"))
    language = models.CharField(max_length=10, default='ar', verbose_name=_("Language"))
    has_completed_profile = models.BooleanField(default=False)

    def __str__(self):
        return f"Profile for {self.company.name}"

    class Meta:
        verbose_name = _("Company Profile")
        verbose_name_plural = _("Company Profiles")

# موديل صفحات النظام لا يحتاج إلى تعديل في هذه المرحلة
class SystemPage(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name=_("Page Name"))
    icon_class = models.CharField(max_length=50, verbose_name=_("Icon Class"))
    allowed_groups = models.ManyToManyField(Group, blank=True, verbose_name=_("Allowed Groups"))
    category = models.CharField(max_length=100, default='General', verbose_name=_("Category"))
    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("System Page")
        verbose_name_plural = _("System Pages")