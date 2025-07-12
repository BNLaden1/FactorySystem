# operations/models.py

from django.db import models
from django.db.models import Sum, F
from accounts.models import Client

# ===================================================================
# 1. تعريف نموذج المشروع (لا تغيير عليه)
# ===================================================================
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

    def total_contract_value(self):
        """يحسب إجمالي قيمة العقد (التكلفة + هامش الربح)"""
        total = self.cost_items.aggregate(
            total=Sum(
                F('quantity') * (F('unit_price') + F('profit_margin')),
                output_field=models.DecimalField()
            )
        )['total']
        return total or 0
    

    def total_costs(self):

        total = self.cost_items.aggregate(
            total=Sum(F('quantity') * F('unit_price'), output_field=models.DecimalField())
        )['total']
        return total or 0

    def total_payments(self):

        result = self.payments.aggregate(total=Sum('amount'))
        return result['total'] or 0

    def remaining_balance(self):
        return self.total_costs() - self.total_payments()

    class Meta:
        verbose_name = "مشروع"
        verbose_name_plural = "المشاريع"

    def __str__(self):
        return self.name

# ===================================================================
# 2. تعريف نموذج أنواع التكاليف (هذا هو الجزء الجديد)
# ===================================================================
class CostType(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="اسم النوع")

    class Meta:
        verbose_name = "نوع تكلفة"
        verbose_name_plural = "أنواع التكاليف"

    def __str__(self):
        return self.name

# ===================================================================
# 3. تعديل نموذج بنود التكاليف (هذا هو الجزء الذي تم تعديله)
# ===================================================================
class CostItem(models.Model):
    project = models.ForeignKey(Project, related_name='cost_items', on_delete=models.CASCADE, verbose_name="المشروع")
    type = models.ForeignKey(CostType, on_delete=models.PROTECT, verbose_name="النوع")
    date = models.DateField(verbose_name="التاريخ")
    description = models.CharField(max_length=255, blank=True, null=True, verbose_name="البيان")
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1, verbose_name="الكمية")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="سعر الوحدة")
    
    # ▼▼▼ هذا هو السطر المفقود الذي سبب المشكلة ▼▼▼
    profit_margin = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="هامش الربح")

    @property
    def total_price(self):
        # الإجمالي الآن سيشمل الربح
        return self.quantity * (self.unit_price + self.profit_margin)

    class Meta:
        verbose_name = "بند تكلفة"
        verbose_name_plural = "بنود التكاليف"

    def __str__(self):
        return self.description

# ===================================================================
# 4. تعريف نموذج الدفعات (لا تغيير عليه)
# ===================================================================
class Payment(models.Model):
    project = models.ForeignKey(Project, related_name='payments', on_delete=models.CASCADE, verbose_name="المشروع")
    date = models.DateField(verbose_name="تاريخ الدفعة")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="المبلغ المدفوع")
    description = models.CharField(max_length=255, blank=True, null=True, verbose_name="بيان الدفعة")
    
    class Meta:
        verbose_name = "دفعة"; verbose_name_plural = "الدفعات"
    def __str__(self): return f"دفعة بقيمة {self.amount} للمشروع {self.project.name}"
