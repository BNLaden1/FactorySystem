from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Project
from .forms import ProjectForm, CostItemForm, PaymentForm 

# 1. دالة عرض قائمة المشاريع
@login_required
def project_list_view(request):
    projects = Project.objects.all()
    context = {
        'projects': projects
    }
    return render(request, 'operations/project_list.html', context)


# 2. دالة إضافة مشروع جديد
@login_required
def add_project_view(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            # الخطوة 1: نحفظ المشروع أولاً للحصول على ID خاص به
            new_project = form.save()
            
            # لاحقاً، سنضيف هنا كود حفظ بنود التكاليف والدفعات
            
            messages.success(request, f'تم إنشاء المشروع "{new_project.name}" بنجاح. يمكنك الآن إضافة تفاصيل التكاليف والدفعات.')
            # سنقوم بتوجيه المستخدم لصفحة تعديل المشروع (سننشئها لاحقاً)
            # حالياً، سنوجهه لقائمة المشاريع
            return redirect('operations:project-list') 
        else:
            messages.error(request, 'حدث خطأ، يرجى مراجعة بيانات المشروع الأساسية.')
    else:
        form = ProjectForm()

    context = {
        'form': form,
        'page_title': 'إنشاء مشروع جديد' # يمكننا استخدام هذا في عنوان الصفحة
    }
    # سنستخدم نفس ملف الواجهة السابق مؤقتاً
    return render(request, 'operations/add_project.html', context)

# operations/views.py

# ▼▼▼ تأكد من إضافة هذا السطر في قسم الـ import بأعلى الملف ▼▼▼
from django.forms import modelformset_factory

# ... (باقي أكواد الـ import والدوال الأخرى تبقى كما هي) ...


# ▼▼▼ أضف هذه الدالة الجديدة كلياً في نهاية الملف ▼▼▼
@login_required
def bulk_add_projects_view(request):
    # نستخدم formset factory لإنشاء مجموعة نماذج من نموذج المشروع
    # extra=5 تعني أننا سنعرض 5 صفوف فارغة للإدخال
    ProjectFormSet = modelformset_factory(Project, form=ProjectForm, extra=1)

    if request.method == 'POST':
        formset = ProjectFormSet(request.POST)
        if formset.is_valid():
            formset.save() # تقوم بحفظ كل النماذج التي تم ملؤها
            messages.success(request, 'تمت إضافة المشاريع بنجاح!')
            return redirect('operations:project-list')
        else:
             messages.error(request, 'يرجى مراجعة البيانات المدخلة، هناك خطأ ما.')
    else:
        formset = ProjectFormSet(queryset=Project.objects.none())

    context = {
        'formset': formset,
        'page_title': 'إضافة مجموعة مشاريع'
    }
    return render(request, 'operations/bulk_add_projects.html', context)

@login_required
def project_detail_view(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if request.method == 'POST':
        # نتحقق من نوع الفورم الذي تم إرساله
        form_type = request.POST.get('form_type')

        if form_type == 'cost_item':
            cost_form = CostItemForm(request.POST)
            if cost_form.is_valid():
                new_cost_item = cost_form.save(commit=False)
                new_cost_item.project = project
                new_cost_item.save()
                messages.success(request, 'تمت إضافة بند التكلفة بنجاح.')
            else:
                messages.error(request, 'حدث خطأ في بيانات بند التكلفة.')

        elif form_type == 'payment':
            payment_form = PaymentForm(request.POST)
            if payment_form.is_valid():
                new_payment = payment_form.save(commit=False)
                new_payment.project = project
                new_payment.save()
                messages.success(request, 'تمت إضافة الدفعة بنجاح.')
            else:
                messages.error(request, 'حدث خطأ في بيانات الدفعة.')
        
        # في كل الحالات، نعيد تحميل نفس الصفحة
        return redirect('operations:project-detail', project_id=project.id)
    
    # هذا الجزء يعمل دائماً، في حالة فتح الصفحة لأول مرة (GET)
    cost_items = project.cost_items.all().order_by('-date')
    payments = project.payments.all().order_by('-date')
    
    # ننشئ فورمات فارغة لعرضها في الصفحة
    cost_form = CostItemForm()
    payment_form = PaymentForm()

    context = {
        'project': project,
        'cost_items': cost_items,
        'payments': payments,
        'cost_form': cost_form,
        'payment_form': payment_form, # <<< نرسل فورم الدفعات للواجهة
        'page_title': f"تفاصيل مشروع: {project.name}"
    }

    return render(request, 'operations/project_detail.html', context)