from django.db import models
from accounts.models import Client, Item # نستدعي نماذج العميل والصنف من تطبيق الحسابات

class Job(models.Model):
    """
    يمثل هذا النموذج "الشغلانة" أو "أمر العمل" لعميل معين.
    """
    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name="العميل")
    job_name = models.CharField(max_length=255, verbose_name="اسم الشغلانة / المشروع")
    description = models.TextField(blank=True, null=True, verbose_name="وصف الشغلانة")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    is_completed = models.BooleanField(default=False, verbose_name="هل اكتملت؟")

    class Meta:
        verbose_name = "شغلانة"
        verbose_name_plural = "الشغلانات"

    def __str__(self):
        return f"شغلانة '{self.job_name}' للعميل '{self.client.name}'"


class JobCost(models.Model):
    """
    يمثل هذا النموذج أي تكلفة فردية يتم إضافتها على شغلانة معينة.
    """
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="costs", verbose_name="الشغلانة")
    item = models.ForeignKey(Item, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="الصنف من المخزون")
    description = models.CharField(max_length=255, verbose_name="وصف بند التكلفة")
    quantity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="الكمية")
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="تكلفة الوحدة")
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, editable=False, verbose_name="التكلفة الإجمالية")

    class Meta:
        verbose_name = "تكلفة شغلانة"
        verbose_name_plural = "تكاليف الشغلانات"

    def save(self, *args, **kwargs):
        # حساب التكلفة الإجمالية تلقائياً قبل الحفظ
        self.total_cost = self.quantity * self.unit_cost
        super().save(*args, **kwargs)

    def __str__(self):
        return f"تكلفة '{self.description}' للشغلانة '{self.job.job_name}'"