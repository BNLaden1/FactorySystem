from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
import json
from datetime import date
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import Group
from django.middleware.csrf import get_token
from django.db import transaction

# (!!!) تأكد من أن هذا السطر يستدعي كل الموديلات الصحيحة (!!!)
from .models import User, Company, Subscription, CompanyProfile, SystemPage, Item
from datetime import timedelta
from django.utils import timezone
from .models import IPRegistrationRecord, Group


# --- دوال مساعدة للتحقق من الصلاحيات ---
def is_superuser(user):
    return user.is_superuser

def is_company_admin(user):
    return user.is_authenticated and user.is_staff and not user.is_superuser


# --- دوال التسجيل والدخول ---
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
            user = User.objects.get(username=username)
            if not user.check_password(password):
                return JsonResponse({'success': False, 'message': 'اسم المستخدم أو كلمة المرور غير صحيحة.'})
            if user.is_superuser:
                login(request, user)
                return JsonResponse({'success': True, 'redirect_url': '/accounts/dashboard/'})
            if not user.is_active:
                return JsonResponse({'success': False, 'message': 'حسابك غير مفعل، يرجى تفعيله أولاً أو التواصل مع الدعم.'})
            subscription = Subscription.objects.get(company=user.company)
            if not subscription.is_active:
                return JsonResponse({'success': False, 'message': 'اشتراك الشركة غير فعال أو منتهي.'})
            login(request, user)
            return JsonResponse({'success': True, 'redirect_url': '/accounts/dashboard/'})
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'اسم المستخدم أو كلمة المرور غير صحيحة.'})
        except Subscription.DoesNotExist:
             return JsonResponse({'success': False, 'message': 'لم يتم العثور على اشتراك لهذه الشركة.'})
        except Exception:
             return JsonResponse({'success': False, 'message': 'حدث خطأ ما.'})
    return render(request, 'accounts/login.html')

def register_view(request):
    # (هنا سيكون منطق التسجيل الذكي مع الفترة التجريبية)
    return render(request, 'accounts/register.html')

def logout_view(request):
    logout(request)
    return redirect('login')

def activate_account_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            serial_number = data.get('serial_number')

            user = User.objects.get(username=username)
            if not user.company:
                 return JsonResponse({'success': False, 'message': 'تفاصيل الحساب غير صحيحة.'})

            subscription = Subscription.objects.get(company=user.company, serial_number=serial_number)
            
            if subscription.is_active:
                return JsonResponse({'success': False, 'message': 'هذا الاشتراك مفعل بالفعل.'})
            
            subscription.activate()
            user.is_active = True
            user.save()

            return JsonResponse({'success': True, 'message': 'تم تفعيل الاشتراك بنجاح! يمكنك الآن تسجيل الدخول.'})

        except (User.DoesNotExist, Subscription.DoesNotExist):
            return JsonResponse({'success': False, 'message': 'اسم المستخدم أو السيريال نمبر غير صحيح.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'حدث خطأ: {str(e)}'})
            
    return JsonResponse({'success': False, 'message': 'طلب غير صالح.'})


# --- دوال لوحة التحكم وملف الشركة ---
@login_required
def dashboard_view(request):
    # لا تغيير على هذا الجزء
    if not request.user.company and not request.user.is_superuser:
        messages.error(request, _("حسابك غير مرتبط بأي شركة."))
        return redirect('logout')

    # المنطق الخاص بالمدير العام
    if request.user.is_superuser:
        context = {
            'company_name': "Superuser Dashboard",
            'today_date': date.today().strftime('%d/%m/%Y'),
            'subscription_days': "N/A",
            'show_profile_popup': False
        }
        return render(request, 'accounts/dashboard.html', context)

    # --- المنطق الجديد والمحصن لمدير الشركة ---
    company = request.user.company
    subscription = None  # القيمة الافتراضية في حالة عدم وجود اشتراك
    profile = None
    show_popup = False

    # -- هذا هو الجزء الذي تم إصلاحه --
    # نحاول العثور على الاشتراك، وإذا لم نجده، نستمر بدون خطأ
    try:
        subscription = Subscription.objects.get(company=company)
    except Subscription.DoesNotExist:
        pass # تجاهل الخطأ والمتابعة

    # نبحث عن ملف الشركة، وإذا لم نجده ننشئه
    profile, created = CompanyProfile.objects.get_or_create(company=company)
    
    # نتحقق إذا كان ملف الشركة غير مكتمل
    if not profile.has_completed_profile:
        show_popup = True
    
    context = {
        'company_name': company.name,
        'today_date': date.today().strftime('%d/%m/%Y'),
        'subscription_days': subscription.remaining_days if subscription else "غير مفعل",
        'show_profile_popup': show_popup,
        'profile': profile,
    }
    return render(request, 'accounts/dashboard.html', context)

@login_required
def update_company_profile_view(request):
    if request.method == 'POST':
        try:
            profile = CompanyProfile.objects.get(company=request.user.company)
            data = json.loads(request.body)
            
            classification = data.get('classification')
            country = data.get('country')

            # التحقق من أن البيانات ليست فارغة في الخلفية
            if not classification or not country or not country.strip():
                return JsonResponse({'success': False, 'message': 'يرجى التأكد من إدخال جميع الحقول المطلوبة.'})

            profile.classification = classification
            profile.country = country
            profile.has_completed_profile = True # أهم خطوة لمنع ظهور النافذة مرة أخرى
            profile.save()
            
            return JsonResponse({'success': True, 'message': 'تم حفظ البيانات بنجاح! جاري تحديث الصفحة...'})
        except CompanyProfile.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'لم يتم العثور على ملف الشركة.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'حدث خطأ: {str(e)}'})
    
    return JsonResponse({'success': False, 'message': 'طلب غير صالح.'}, status=400)

# --- دوال إدارة الموظفين ---
@login_required
@user_passes_test(is_company_admin, login_url='/accounts/login/')
def manage_employees_view(request):
    employees = User.objects.filter(company=request.user.company, is_staff=False).order_by('username')
    context = {'employees_list': employees}
    return render(request, 'accounts/manage_employees.html', context)

@login_required
@user_passes_test(is_company_admin, login_url='/accounts/login/')
def edit_employee_permissions_view(request, employee_id):
    employee = get_object_or_404(User, id=employee_id, company=request.user.company)
    top_level_pages = SystemPage.objects.filter(parent__isnull=True).prefetch_related('children')
    try:
        employee_group = employee.groups.get(name=f"EmployeeGroup_{employee.id}")
        employee_permissions = employee_group.system_pages.all()
    except Group.DoesNotExist:
        employee_permissions = []
    context = {
        'employee': employee,
        'top_level_pages': top_level_pages,
        'employee_permissions': employee_permissions,
    }
    return render(request, 'accounts/edit_employee_permissions.html', context)

# --- هذه هي الدالة التي كانت مفقودة ---
@login_required
@user_passes_test(is_company_admin, login_url='/accounts/login/')
def save_employee_permissions_view(request, employee_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            page_id = data.get('page_id')
            is_active = data.get('is_active')
            employee = get_object_or_404(User, id=employee_id, company=request.user.company)
            page = get_object_or_404(SystemPage, id=page_id)
            group_name = f"EmployeeGroup_{employee.id}"
            employee_group, created = Group.objects.get_or_create(name=group_name)
            if is_active:
                employee_group.system_pages.add(page)
            else:
                employee_group.system_pages.remove(page)
            employee.groups.add(employee_group)
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


# --- دوال الإدارة للمدير العام ---
@user_passes_test(is_superuser)
def manage_users_view(request):
    users = User.objects.all().order_by('company__name')
    context = {'users_list': users}
    return render(request, 'accounts/manage_users.html', context)

@user_passes_test(is_superuser)
def manage_subscriptions_view(request):
    subscriptions = Subscription.objects.all()
    context = {'subscriptions_list': subscriptions}
    return render(request, 'accounts/manage_subscriptions.html', context)


# --- الدوال المؤقتة للصفحات الأخرى (Coming Soon) ---
@login_required
def sales_page_view(request): return render(request, 'accounts/coming_soon.html', {'page_title': 'المبيعات'})
@login_required
def clients_page_view(request): return render(request, 'accounts/coming_soon.html', {'page_title': 'العملاء'})
@login_required
def quotes_page_view(request): return render(request, 'accounts/coming_soon.html', {'page_title': 'عروض الأسعار'})
@login_required
def logistics_page_view(request): return render(request, 'accounts/coming_soon.html', {'page_title': 'المناديب والمخازن'})
@login_required
def purchases_page_view(request): return render(request, 'accounts/coming_soon.html', {'page_title': 'المشتريات'})
@login_required
def items_page_view(request):
    # التأكد من أن المستخدم مدير شركة أو موظف له صلاحية
    if not request.user.company:
        return redirect('dashboard') # أو أي صفحة خطأ مناسبة

    items = Item.objects.filter(company=request.user.company).order_by('name')
    context = {
        'items_list': items, #
        'page_name': 'items_page'
    }
    return render(request, 'accounts/items.html', context)
@login_required
def upload_excel_page_view(request): return render(request, 'accounts/coming_soon.html', {'page_title': 'رفع ملف إكسل'})
@login_required
def transactions_page_view(request): return render(request, 'accounts/coming_soon.html', {'page_title': 'مصروفات وإيرادات'})
@login_required
def messages_page_view(request): return render(request, 'accounts/coming_soon.html', {'page_title': 'الرسائل'})
@login_required
def hr_page_view(request): return render(request, 'accounts/coming_soon.html', {'page_title': 'الموظفين والرواتب'})
@login_required
def reports_page_view(request): return render(request, 'accounts/coming_soon.html', {'page_title': 'التقارير'})
@login_required
def pos_page_view(request): return render(request, 'accounts/coming_soon.html', {'page_title': 'الخزن / نقاط البيع'})
@login_required
def settings_page_view(request): return render(request, 'accounts/coming_soon.html', {'page_title': 'الإعدادات'})
# في نهاية ملف accounts/views.py

@login_required
@user_passes_test(is_company_admin, login_url='/accounts/login/')
def add_employee_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
            email = data.get('email')

            if not username or not password:
                return JsonResponse({'success': False, 'message': 'اسم المستخدم وكلمة المرور حقول إجبارية.'})

            if User.objects.filter(username=username).exists():
                return JsonResponse({'success': False, 'message': 'اسم المستخدم هذا مسجل بالفعل.'})

            new_employee = User.objects.create_user(
                username=username,
                password=password,
                email=email,
                company=request.user.company,
                is_staff=False,
                is_active=True
            )
            
            return JsonResponse({'success': True, 'message': 'تمت إضافة الموظف بنجاح!'})

        except Exception as e:
            return JsonResponse({'success': False, 'message': f'حدث خطأ غير متوقع: {str(e)}'})
    
    return redirect('manage_employees')

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        # 1. التحقق من الـ IP لمنع التسجيل المكرر
        client_ip = get_client_ip(request)
        if IPRegistrationRecord.objects.filter(ip_address=client_ip).exists():
            return JsonResponse({'success': False, 'message': 'لقد قمت بالتسجيل من هذا الجهاز بالفعل للحصول على فترة تجريبية.'})
            
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
            company_name = data.get('company_name')
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'خطأ في البيانات المرسلة.'}, status=400)

        if not all([username, password, company_name]):
            return JsonResponse({'success': False, 'message': 'يرجى ملء جميع الحقول.'})

        if User.objects.filter(username=username).exists():
            return JsonResponse({'success': False, 'message': 'اسم المستخدم هذا مسجل بالفعل.'})
        
        if Company.objects.filter(name=company_name).exists():
            return JsonResponse({'success': False, 'message': 'اسم الشركة هذا مسجل بالفعل.'})

        # 2. إنشاء الشركة والمستخدم والاشتراك التجريبي
        company = Company.objects.create(name=company_name)
        user = User.objects.create_user(username=username, password=password, company=company, is_active=True, is_staff=True)
        
        subscription = Subscription.objects.create(company=company, is_active=True)
        subscription.start_date = timezone.now().date()
        subscription.end_date = timezone.now().date() + timedelta(days=3) # فترة تجريبية 3 أيام
        subscription.save()

        CompanyProfile.objects.create(company=company)
        IPRegistrationRecord.objects.create(ip_address=client_ip, company=company)
        
        # 3. إعطاء مدير الشركة صلاحيات كاملة تلقائياً
        try:
            manager_group, created = Group.objects.get_or_create(name='مدراء الشركات')
            if created:
                # إذا كانت المجموعة جديدة، نمنحها كل الصلاحيات
                all_pages = SystemPage.objects.all()
                manager_group.system_pages.set(all_pages)
            user.groups.add(manager_group)
        except Exception as e:
            print(f"Could not assign default permissions: {e}")

        return JsonResponse({'success': True, 'message': 'تم إنشاء حسابك التجريبي بنجاح! سيتم توجيهك الآن لتسجيل الدخول.'})

    return render(request, 'accounts/register.html')

@login_required
@user_passes_test(is_company_admin, login_url='/accounts/login/')
def delete_employee_view(request, employee_id):
    if request.method == 'POST':
        try:
            # نتأكد أن الموظف المطلوب حذفه يتبع لنفس شركة المدير
            employee_to_delete = get_object_or_404(User, id=employee_id, company=request.user.company)
            
            # لا نسمح للمدير بحذف نفسه
            if employee_to_delete == request.user:
                return JsonResponse({'success': False, 'message': 'لا يمكنك حذف حسابك.'})

            employee_to_delete.delete()
            return JsonResponse({'success': True, 'message': 'تم حذف الموظف بنجاح.'})

        except Exception as e:
            return JsonResponse({'success': False, 'message': f'حدث خطأ: {str(e)}'})
    
    return JsonResponse({'success': False, 'message': 'طلب غير صالح.'})

@login_required
@transaction.atomic # <-- هذا يضمن حفظ كل الأصناف معاً أو عدم حفظ أي شيء
def add_item_view(request):
    if not request.user.company:
        return JsonResponse({'success': False, 'message': 'طلب غير مصرح به.'})

    if request.method == 'POST':
        try:
            items_data = json.loads(request.body)
            
            # سنتعامل الآن مع قائمة من الأصناف وليس صنفا واحدا
            for item_data in items_data:
                Item.objects.create(
                    company=request.user.company,
                    name=item_data.get('name'),
                    code=item_data.get('code'),
                    price=item_data.get('price'),
                    cost=item_data.get('cost'),
                    quantity=item_data.get('quantity')
                )
            
            return JsonResponse({'success': True, 'message': 'تمت إضافة الأصناف بنجاح!'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'حدث خطأ: {str(e)}'})
    
    return redirect('items_page')

@login_required
def delete_item_view(request, item_id):
    if request.method == 'POST':
        try:
            # نتأكد أن الصنف المطلوب حذفه يتبع لنفس شركة المستخدم
            item_to_delete = get_object_or_404(Item, id=item_id, company=request.user.company)
            item_to_delete.delete()
            return JsonResponse({'success': True, 'message': 'تم حذف الصنف بنجاح.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'حدث خطأ: {str(e)}'})
    
    return JsonResponse({'success': False, 'message': 'طلب غير صالح.'})