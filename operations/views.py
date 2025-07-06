from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Project
from .forms import ProjectForm, CostItemForm

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

    # هذا الجزء سيتعامل مع الفورم عند إرسال البيانات (POST)
    if request.method == 'POST':
        cost_form = CostItemForm(request.POST)
        if cost_form.is_valid():
            # لا نحفظ الفورم مباشرة، بل نجهز البيانات أولاً
            new_cost_item = cost_form.save(commit=False)
            # نربط بند التكلفة الجديد بالمشروع الحالي
            new_cost_item.project = project
            new_cost_item.save() # الآن نقوم بالحفظ
            messages.success(request, 'تمت إضافة بند التكلفة بنجاح.')
            # نعيد تحميل نفس الصفحة لنرى البند الجديد في الجدول
            return redirect('operations:project-detail', project_id=project.id)
        else:
            messages.error(request, 'حدث خطأ في بيانات بند التكلفة.')
    
    # هذا الجزء يعمل دائماً، سواء كان الطلب GET أو POST فاشل
    cost_items = project.cost_items.all().order_by('-date')
    payments = project.payments.all().order_by('-date')
    
    # ننشئ فورم فارغ لعرضه في الصفحة
    cost_form = CostItemForm()

    context = {
        'project': project,
        'cost_items': cost_items,
        'payments': payments,
        'cost_form': cost_form, # <<< نرسل الفورم الفارغ للواجهة
        'page_title': f"تفاصيل مشروع: {project.name}"
    }

    return render(request, 'operations/project_detail.html', context)
