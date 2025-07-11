# operations/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.forms import modelformset_factory
from django.forms import inlineformset_factory


from .models import Project, CostItem, Payment, CostType
from .forms import ProjectForm, CostItemForm, PaymentForm

# 1. دالة عرض قائمة المشاريع
@login_required
def project_list_view(request):
    projects = Project.objects.all().order_by('-start_date')
    context = {
        'projects': projects,
        'page_title': 'قائمة المشاريع'
    }
    return render(request, 'operations/project_list.html', context)

# 2. دالة إضافة مشروع واحد
@login_required
def add_project_view(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            new_project = form.save()
            messages.success(request, f'تم إنشاء المشروع "{new_project.name}" بنجاح.')
            return redirect('operations:project-detail', project_id=new_project.id)
    else:
        form = ProjectForm()
    context = {
        'form': form,
        'page_title': 'إنشاء مشروع جديد'
    }
    return render(request, 'operations/add_project.html', context)

# 3. دالة الإضافة المجمعة
@login_required
def bulk_add_projects_view(request):
    ProjectFormSet = modelformset_factory(Project, form=ProjectForm, extra=1)
    if request.method == 'POST':
        formset = ProjectFormSet(request.POST)
        if formset.is_valid():
            formset.save()
            messages.success(request, 'تمت إضافة المشاريع بنجاح!')
            return redirect('operations:project-list')
    else:
        formset = ProjectFormSet(queryset=Project.objects.none())
    context = {
        'formset': formset,
        'page_title': 'إضافة مجموعة مشاريع'
    }
    return render(request, 'operations/bulk_add_projects.html', context)

# 4. دالة تفاصيل المشروع
@login_required
def project_detail_view(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    # هذا الجزء الآن يتعامل فقط مع فورم إضافة "بند تكلفة" جديد
    if request.method == 'POST':
        # نتحقق إذا كان المستخدم يضيف بند تكلفة
        if 'save_cost_item' in request.POST:
            cost_form = CostItemForm(request.POST)
            if cost_form.is_valid():
                new_item = cost_form.save(commit=False)
                new_item.project = project
                new_item.save()
                messages.success(request, 'تمت إضافة بند التكلفة بنجاح.')
            else:
                # الآن سنعرض الأخطاء المحددة
                for field, errors in cost_form.errors.items():
                    for error in errors:
                        messages.error(request, f"خطأ في حقل '{cost_form.fields[field].label}': {error}")

        # أو إذا كان يضيف دفعة
        elif 'save_payment' in request.POST:
            payment_form = PaymentForm(request.POST)
            if payment_form.is_valid():
                new_payment = payment_form.save(commit=False)
                new_payment.project = project
                new_payment.save()
                messages.success(request, 'تمت إضافة الدفعة بنجاح.')
            else:
                messages.error(request, 'حدث خطأ في بيانات الدفعة.')

        return redirect('operations:project-detail', project_id=project.id)

    # نجهز البيانات لعرضها في الصفحة
    cost_form = CostItemForm()
    payment_form = PaymentForm()
    cost_items = project.cost_items.all().order_by('date')
    payments = project.payments.all().order_by('-date')
    other_projects = Project.objects.filter(client=project.client).exclude(id=project.id).order_by('-start_date')
    quick_access_projects = other_projects.filter(status='قيد التنفيذ')[:4]

    context = {
        'project': project,
        'cost_form': cost_form,
        'cost_items': cost_items,
        'payments': payments,
        'payment_form': payment_form,
        'other_projects': other_projects,
        'quick_access_projects': quick_access_projects,
        'page_title': f"تفاصيل مشروع: {project.name}"
    }

    return render(request, 'operations/project_detail.html', context)


    # --- هذا هو الجزء التشخيصي والحل ---
    # 1. سنقوم بجلب البنود المحفوظة بشكل صريح
    items_queryset = CostItem.objects.filter(project=project).order_by('date')

    # 2. سنقوم بطباعة هذه البيانات في شاشة الأوامر (Terminal) للتأكد
    print("----------- DIAGNOSTIC INFO -----------")
    print(f"Fetching items for Project ID: {project.id}")
    print(f"Found {items_queryset.count()} items.")
    for item in items_queryset:
        print(f"  - Item ID: {item.id}, Description: {item.description}")
    print("---------------------------------------")

    # 3. سنقوم بإنشاء الفورم مع تمرير البيانات التي جلبناها بشكل صريح
    cost_formset = CostItemFormSet(instance=project, queryset=items_queryset, prefix='costs')

    # --- نهاية الجزء التشخيصي والحل ---

    payment_form = PaymentForm()
    payments = project.payments.all().order_by('-date')
    other_projects = Project.objects.filter(client=project.client).exclude(id=project.id).order_by('-start_date')
    quick_access_projects = other_projects.filter(status='قيد التنفيذ')[:4]

    context = {
        'project': project,
        'cost_formset': cost_formset,
        'payments': payments,
        'payment_form': payment_form,
        'other_projects': other_projects,
        'quick_access_projects': quick_access_projects,
        'page_title': f"تفاصيل مشروع: {project.name}"
    }

    return render(request, 'operations/project_detail.html', context)


# 5. دالة تغيير حالة المشروع
@login_required
def set_project_status_view(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status:
            project.status = new_status
            project.save()
            messages.success(request, f'تم تغيير حالة المشروع إلى "{new_status}" بنجاح.')
    return redirect('operations:project-detail', project_id=project.id)

# 6. ▼▼▼ هذه هي الدالة التي كانت مفقودة ▼▼▼
@login_required
def manage_cost_types_view(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        if name:
            CostType.objects.get_or_create(name=name)
            messages.success(request, f'تمت إضافة النوع "{name}" بنجاح.')
        else:
            messages.error(request, 'لا يمكن إضافة نوع فارغ.')
        return redirect('operations:cost-type-manage')
    all_types = CostType.objects.all().order_by('name')
    context = {
        'cost_types': all_types,
        'page_title': 'إدارة أنواع التكاليف'
    }
    return render(request, 'operations/manage_cost_types.html', context)

@login_required
def delete_cost_item_view(request, item_id):
    # نبحث عن البند المطلوب حذفه
    item = get_object_or_404(CostItem, id=item_id)
    # نحفظ رقم المشروع قبل الحذف لنعود لنفس الصفحة
    project_id = item.project.id 
    # نقوم بالحذف
    item.delete()
    # نرسل رسالة نجاح
    messages.success(request, 'تم حذف بند التكلفة بنجاح.')
    # نعود لصفحة تفاصيل المشروع
    return redirect('operations:project-detail', project_id=project_id)

@login_required
def delete_payment_view(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)
    project_id = payment.project.id # نحفظ رقم المشروع قبل حذف الدفعة
    payment.delete()
    messages.success(request, 'تم حذف الدفعة بنجاح.')
    return redirect('operations:project-detail', project_id=project_id)

@login_required
def edit_payment_view(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)
    project_id = payment.project.id
    if request.method == 'POST':
        # نمرر 'instance=payment' ليقوم الفورم بتحديث الدفعة الحالية بدلاً من إنشاء واحدة جديدة
        form = PaymentForm(request.POST, instance=payment)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تعديل الدفعة بنجاح.')
        else:
            messages.error(request, 'حدث خطأ أثناء تعديل الدفعة.')
    # في كل الحالات، ارجع لصفحة تفاصيل المشروع
    return redirect('operations:project-detail', project_id=project_id)