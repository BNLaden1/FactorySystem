# operations/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CostItem, Payment

# هذا هو "جرس الإنذار" الأول الذي يرن بعد حفظ أي "بند تكلفة"
@receiver(post_save, sender=CostItem)
def update_status_on_new_cost(sender, instance, created, **kwargs):
    """
    عند إضافة أول بند تكلفة لمشروع جديد، يتم تغيير حالته إلى "قيد التنفيذ".
    """
    # "created" تكون True فقط عند إنشاء البند لأول مرة
    if created:
        project = instance.project
        if project.status == 'جديد':
            project.status = 'قيد التنفيذ'
            project.save()


# هذا هو "جرس الإنذار" الثاني الذي يرن بعد حفظ أي "دفعة"
@receiver(post_save, sender=Payment)
def update_status_on_payment(sender, instance, **kwargs):
    """
    عندما يصل إجمالي المدفوعات لإجمالي التكاليف، يتم تغيير حالة المشروع إلى "مكتمل".
    """
    project = instance.project
    # نتأكد أن المشروع ليس جديداً أو ملغياً
    if project.status not in ['جديد', 'ملغي', 'مكتمل']:
        # نستخدم الدالة التي أنشأناها في a_models.py لحساب المتبقي
        if project.remaining_balance() <= 0:
            project.status = 'مكتمل'
            project.save()