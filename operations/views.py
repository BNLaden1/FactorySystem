from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Project
from .forms import ProjectForm

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
    # الخطوة 1: نجلب المشروع المحدد من قاعدة البيانات
    # إذا لم يكن المشروع موجوداً، ستظهر صفحة خطأ 404 تلقائياً
    project = get_object_or_404(Project, id=project_id)

    # الخطوة 2: نجلب كل بنود التكاليف والدفعات المرتبطة بهذا المشروع
    cost_items = project.cost_items.all().order_by('-date')
    payments = project.payments.all().order_by('-date')

    # الخطوة 3: نجهز البيانات لإرسالها للواجهة
    context = {
        'project': project,
        'cost_items': cost_items,
        'payments': payments,
        'page_title': f"تفاصيل مشروع: {project.name}"
    }

    # نحدد ملف الواجهة الذي سيعرض هذه البيانات
    return render(request, 'operations/project_detail.html', context)
