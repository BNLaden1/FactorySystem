# employees/admin.py
from django.contrib import admin
from .models import Attendance

# هذا السطر يخبر جانغو بإظهار نموذج الحضور في لوحة التحكم
admin.site.register(Attendance)