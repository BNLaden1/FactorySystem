# operations/forms.py

from django import forms
from .models import Project, CostItem, Payment, CostType
from accounts.models import Client
import datetime


class ProjectForm(forms.ModelForm):
    # هذا السطر مهم لجلب العملاء من قاعدة البيانات وعرضهم في قائمة منسدلة
    client = forms.ModelChoiceField(
        queryset=Client.objects.all(),
        label="العميل",
        empty_label="-- اختر العميل --",
        widget=forms.Select(attrs={'class': 'block w-full p-2 border border-gray-300 rounded-lg bg-gray-50 text-sm focus:ring-blue-500 focus:border-blue-500'})
    )

    class Meta:
        model = Project
        # ▼▼▼ نستخدم هنا أسماء الحقول الجديدة والصحيحة فقط ▼▼▼
        fields = ['client', 'name', 'start_date', 'due_date', 'status']

        # نضيف عناوين عربية للحقول (labels)
        labels = {
            'name': 'اسم الأوردر/المشروع',
            'start_date': 'تاريخ البدء',
            'due_date': 'تاريخ التسليم المتوقع',
            'status': 'الحالة',
        }
        
        # نحدد التنسيقات (CSS classes) لكل حقل
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'block w-full p-2 border border-gray-300 rounded-lg bg-gray-50 text-sm focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'مثال: غرفة نوم، مطبخ...'
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'block w-full p-2 border border-gray-300 rounded-lg bg-gray-50 text-sm focus:ring-blue-500 focus:border-blue-500',
                'type': 'date'
            }),
            'due_date': forms.DateInput(attrs={
                'class': 'block w-full p-2 border border-gray-300 rounded-lg bg-gray-50 text-sm focus:ring-blue-500 focus:border-blue-500',
                'type': 'date'
            }),
            'status': forms.Select(attrs={
                'class': 'block w-full p-2 border border-gray-300 rounded-lg bg-gray-50 text-sm focus:ring-blue-500 focus:border-blue-500'
            }),
        }

        # operations/forms.py

# ... (from django import forms و from .models import Project و class ProjectForm تبقى كما هي) ...

# ▼▼▼ أضف هذا الكلاس الجديد في نهاية الملف ▼▼▼
class CostItemForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CostItemForm, self).__init__(*args, **kwargs)
        # ▼▼▼ هذا هو السطر الذي يضع تاريخ اليوم تلقائياً ▼▼▼
        self.fields['date'].initial = datetime.date.today()

    class Meta:
        model = CostItem
        fields = ['date', 'type', 'description', 'quantity', 'unit_price']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'w-full p-2 border rounded-lg text-sm'}),
            'type': forms.Select(attrs={'class': 'w-full p-2 border rounded-lg text-sm'}),
            'description': forms.TextInput(attrs={'class': 'w-full p-2 border rounded-lg text-sm', 'placeholder': 'اكتب بياناً...'}),
            'quantity': forms.NumberInput(attrs={'class': 'w-full p-2 border rounded-lg text-sm'}),
            'unit_price': forms.NumberInput(attrs={'class': 'w-full p-2 border rounded-lg text-sm'}),
        }

# ▼▼▼ أضف هذا الكلاس الجديد في نهاية الملف ▼▼▼
class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        # نحدد الحقول التي نريدها أن تظهر في الفورم
        fields = ['date', 'amount', 'description']

        # نضيف تنسيقات Tailwind CSS للفورم
        widgets = {
            'date': forms.DateInput(attrs={
                'class': 'block w-full p-2 border border-gray-300 rounded-lg bg-gray-50 text-sm focus:ring-blue-500 focus:border-blue-500',
                'type': 'date'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'block w-full p-2 border border-gray-300 rounded-lg bg-gray-50 text-sm focus:ring-blue-500 focus:border-blue-500'
            }),
            'description': forms.TextInput(attrs={
                'class': 'block w-full p-2 border border-gray-300 rounded-lg bg-gray-50 text-sm focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'مثال: دفعة تحت الحساب'
            }),
        }