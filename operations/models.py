# operations/models.py
from django.db import models
from django.db.models import Sum
from accounts.models import Client
from django.db.models import Sum, F

# النموذج الرئيسي للمشروع
class Project(models.Model):
    STATUS_CHOICES = (
        ('جديد', 'جديد'),
        ('قيد التنفيذ', 'قيد التنفيذ'),
        ('متوقف', 'متوقف'),
        ('بانتظار الدفع', 'بانتظار الدفع'),
        ('مكتمل', 'مكتمل'),
        ('ملغي', 'ملغي'),
    )
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, verbose_name="العميل")
    name = models.CharField(max_length=255, verbose_name="اسم الأوردر/المشروع")
    start_date = models.DateField(verbose_name="تاريخ البدء")
    due_date = models.DateField(blank=True, null=True, verbose_name="تاريخ التسليم المتوقع")
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='جديد', verbose_name="الحالة")

    # الخصائص الحسابية (سيتم حسابها تلقائياً)
    def total_costs(self):
        # نطلب من قاعدة البيانات ضرب الكمية في السعر ثم جمع الناتج
        total = self.cost_items.aggregate(
            total=Sum(F('quantity') * F('unit_price'), output_field=models.DecimalField())
        )['total']
        return total or 0

    def total_payments(self):
        # يجمع كل الدفعات التابعة لهذا المشروع
        result = self.payments.aggregate(total=Sum('amount'))
        return result['total'] or 0

    def remaining_balance(self):
        return self.total_costs() - self.total_payments()

    class Meta:
        verbose_name = "مشروع"
        verbose_name_plural = "المشاريع"

    def __str__(self):
        return self.name

# نموذج بنود التكاليف (الجدول الأخضر - جزء التكاليف)
class CostItem(models.Model):
    project = models.ForeignKey(Project, related_name='cost_items', on_delete=models.CASCADE, verbose_name="المشروع")
    date = models.DateField(verbose_name="التاريخ")
    description = models.CharField(max_length=255, verbose_name="البيان (نوع الخامة أو الخدمة)")
    quantity = models.FloatField(default=1, verbose_name="الكمية")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="سعر الوحدة")

    @property
    def total_price(self):
        return self.quantity * self.unit_price

    class Meta:
        verbose_name = "بند تكلفة"
        verbose_name_plural = "بنود التكاليف"

    def __str__(self):
        return self.description

# نموذج الدفعات (الجدول الأخضر - جزء الدفعات)
class Payment(models.Model):
    project = models.ForeignKey(Project, related_name='payments', on_delete=models.CASCADE, verbose_name="المشروع")
    date = models.DateField(verbose_name="تاريخ الدفعة")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="المبلغ المدفوع")
    description = models.CharField(max_length=255, blank=True, null=True, verbose_name="بيان الدفعة")

    class Meta:
        verbose_name = "دفعة"
        verbose_name_plural = "الدفعات"

    def __str__(self):
        return f"دفعة بقيمة {self.amount} للمشروع {self.project.name}"