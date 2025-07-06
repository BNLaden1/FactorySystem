# employees/models.py

from django.db import models
# هذا هو السطر المهم الذي كان ناقصًا، نستدعي به نموذج المستخدم الجاهز
from accounts.models import User 

# نموذج لتسجيل الحضور والغياب اليومي
class Attendance(models.Model):
    STATUS_CHOICES = (
        ('حاضر', 'حاضر'),
        ('غائب', 'غائب'),
        ('أجازة', 'أجازة'),
    )
    # هنا قمنا بربط سجل الحضور بنموذج المستخدم 'User' الموجود بالفعل بدلاً من 'Employee' الوهمي
    employee = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="الموظف")
    date = models.DateField(verbose_name="التاريخ")
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, verbose_name="الحالة")
    notes = models.CharField(max_length=255, blank=True, null=True, verbose_name="ملاحظات")

    def __str__(self):
        return f"{self.employee.username} - {self.date} - {self.status}"

    class Meta:
        verbose_name = "سجل حضور"
        verbose_name_plural = "سجلات الحضور"