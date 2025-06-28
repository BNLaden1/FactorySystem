from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.contrib import messages
from django.utils.translation import gettext as _
import json

# (!!!) هذا هو سطر الـ import الوحيد والصحيح لكل الموديلات (!!!)
from .models import User, Company, Subscription, CompanyProfile, SystemPage


# --- دالة للتحقق من أن المستخدم مدير عام (Superuser) ---
def is_superuser(user):
    return user.is_superuser

# --- دالة تسجيل الدخول (النسخة النهائية والمصححة) ---
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # المدير العام (Superuser) يمكنه الدخول دائماً
            if user.is_superuser:
                login(request, user)
                return JsonResponse({'success': True, 'redirect_url': '/accounts/dashboard/'})

            # بالنسبة للمستخدمين العاديين، يجب أن يكون الحساب والاشتراك فعالين
            if not user.company:
                return JsonResponse({'success': False, 'message': _('This account is not associated with a company.')})

            try:
                subscription = Subscription.objects.get(company=user.company)
                if not user.is_active:
                     return JsonResponse({'success': False, 'message': _('Your account is inactive. Please contact support.')})
                if not subscription.is_active:
                    return JsonResponse({'success': False, 'message': _('The company subscription is inactive.')})
                
                login(request, user)
                return JsonResponse({'success': True, 'redirect_url': '/accounts/dashboard/'})

            except Subscription.DoesNotExist:
                return JsonResponse({'success': False, 'message': _('No subscription found for this company.')})
        else:
            return JsonResponse({'success': False, 'message': _('Invalid username or password.')})
            
    return render(request, 'accounts/login.html')


# --- دالة تسجيل حساب جديد (النسخة النهائية والمصححة) ---
def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        company_name = data.get('company_name')

        if User.objects.filter(username=username).exists():
            return JsonResponse({'success': False, 'message': _('Username already exists.')})
        
        if Company.objects.filter(name=company_name).exists():
            return JsonResponse({'success': False, 'message': _('Company name already exists.')})

        # 1. إنشاء الشركة أولاً
        company = Company.objects.create(name=company_name)
        
        # 2. إنشاء الاشتراك غير المفعل للشركة
        Subscription.objects.create(company=company, is_active=False)

        # 3. إنشاء ملف تعريف الشركة
        CompanyProfile.objects.create(company=company)

        # 4. إنشاء المستخدم (مدير الشركة) وربطه بالشركة
        # يتم إنشاء المستخدم كـ staff ليكون هو مدير الشركة، وحسابه غير مفعل
        user = User.objects.create_user(username=username, password=password, company=company, is_active=False, is_staff=True)
        
        return JsonResponse({'success': True, 'message': _('Account created successfully! Please activate your subscription.')})

    return render(request, 'accounts/register.html')


# --- دالة تفعيل الاشتراك (النسخة النهائية والمصححة) ---
def activate_account_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        serial_number = data.get('serial_number')

        try:
            user = User.objects.get(username=username)
            if not user.company:
                 return JsonResponse({'success': False, 'message': _('Invalid account details.')})

            subscription = Subscription.objects.get(company=user.company, serial_number=serial_number)
            
            if subscription.is_active:
                return JsonResponse({'success': False, 'message': _('Subscription is already active.')})
            
            # تفعيل اشتراك الشركة وتفعيل حساب المستخدم المدير
            subscription.activate()
            user.is_active = True
            user.save()

            return JsonResponse({'success': True, 'message': _('Subscription activated successfully! You can now log in.')})

        except (User.DoesNotExist, Subscription.DoesNotExist):
            return JsonResponse({'success': False, 'message': _('Invalid username or serial number.')})

    return JsonResponse({'success': False, 'message': _('Invalid request.')})


# --- دالة تسجيل الخروج ---
def logout_view(request):
    logout(request)
    return redirect('login')


# --- لوحة التحكم (النسخة النهائية والمصححة) ---
@login_required
def dashboard_view(request):
    if not request.user.company and not request.user.is_superuser:
        messages.error(request, _("Your account is not linked to any company."))
        return redirect('logout')

    company = request.user.company
    subscription = None
    remaining_days = "N/A"
    
    if company:
        try:
            subscription = Subscription.objects.get(company=company)
            remaining_days = subscription.remaining_days
        except Subscription.DoesNotExist:
            pass

    context = {
        'company': company,
        'subscription': subscription,
        'remaining_days': remaining_days
    }
    return render(request, 'accounts/dashboard_standalone.html', context)

# باقي الدوال (coming_soon) يمكن أن تبقى كما هي حالياً...
# --- دوال مؤقتة لصفحات الشريط الجانبي (Coming Soon Pages) ---

@login_required
def sales_page_view(request):
    return render(request, 'accounts/coming_soon.html', {'page_title': 'المبيعات'})

@login_required
def clients_page_view(request):
    return render(request, 'accounts/coming_soon.html', {'page_title': 'العملاء'})

@login_required
def quotes_page_view(request):
    return render(request, 'accounts/coming_soon.html', {'page_title': 'عروض الأسعار'})

@login_required
def logistics_page_view(request):
    return render(request, 'accounts/coming_soon.html', {'page_title': 'المناديب والمخازن'})

@login_required
def purchases_page_view(request):
    return render(request, 'accounts/coming_soon.html', {'page_title': 'المشتريات'})

@login_required
def items_page_view(request):
    return render(request, 'accounts/coming_soon.html', {'page_title': 'الأصناف'})

@login_required
def upload_excel_page_view(request):
    return render(request, 'accounts/coming_soon.html', {'page_title': 'رفع ملف إكسل'})

@login_required
def transactions_page_view(request):
    return render(request, 'accounts/coming_soon.html', {'page_title': 'مصروفات وإيرادات'})

@login_required
def messages_page_view(request):
    return render(request, 'accounts/coming_soon.html', {'page_title': 'الرسائل'})

@login_required
def hr_page_view(request):
    return render(request, 'accounts/coming_soon.html', {'page_title': 'الموظفين والرواتب'})

@login_required
def reports_page_view(request):
    return render(request, 'accounts/coming_soon.html', {'page_title': 'التقارير'})

@login_required
def pos_page_view(request):
    return render(request, 'accounts/coming_soon.html', {'page_title': 'الخزن / نقاط البيع'})

@login_required
def settings_page_view(request):
    return render(request, 'accounts/coming_soon.html', {'page_title': 'الإعدادات'})

# --- دوال الإدارة للمدير العام ---

@user_passes_test(is_superuser)
def manage_users_view(request):
    users = User.objects.all().order_by('company__name')
    context = {'users': users}
    return render(request, 'accounts/manage_users.html', context)

@user_passes_test(is_superuser)
def manage_subscriptions_view(request):
    subscriptions = Subscription.objects.all()
    context = {'subscriptions': subscriptions}
    return render(request, 'accounts/manage_subscriptions.html', context)

@user_passes_test(is_superuser)
def activate_company_subscription_view(request, sub_id):
    subscription = get_object_or_404(Subscription, id=sub_id)
    subscription.activate()
    company_admin = User.objects.filter(company=subscription.company, is_staff=True).first()
    if company_admin:
        company_admin.is_active = True
        company_admin.save()
    messages.success(request, _(f"Subscription for {subscription.company.name} has been activated."))
    return redirect('manage_subscriptions')