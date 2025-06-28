from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.contrib import messages
from django.utils.translation import gettext as _
import json
from datetime import date

# (!!!) تأكد من أن هذا السطر يستدعي كل الموديلات الصحيحة (!!!)
from .models import User, Company, Subscription, CompanyProfile, SystemPage


# --- دالة للتحقق من أن المستخدم مدير عام (Superuser) ---
def is_superuser(user):
    return user.is_superuser

# --- دالة تسجيل الدخول (النسخة النهائية والمصححة) ---
# في ملف accounts/views.py

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'خطأ في البيانات المرسلة.'}, status=400)

        # --- المنطق الجديد والمحسن لتسجيل الدخول ---
        try:
            # 1. ابحث عن المستخدم أولاً
            user = User.objects.get(username=username)
            
            # 2. تحقق من كلمة المرور
            if not user.check_password(password):
                # إذا كانت كلمة المرور خطأ، لا تكمل
                return JsonResponse({'success': False, 'message': 'اسم المستخدم أو كلمة المرور غير صحيحة.'})

            # 3. إذا كانت كلمة المرور صحيحة، تحقق من حالة الحساب والاشتراك
            if user.is_superuser:
                login(request, user)
                return JsonResponse({'success': True, 'redirect_url': '/accounts/dashboard/'})

            if not user.is_active:
                return JsonResponse({'success': False, 'message': 'حسابك غير مفعل، يرجى تفعيله أولاً أو التواصل مع الدعم.'})
            
            # التحقق من اشتراك الشركة
            subscription = Subscription.objects.get(company=user.company)
            if not subscription.is_active:
                return JsonResponse({'success': False, 'message': 'اشتراك الشركة غير فعال أو منتهي.'})

            # 4. كل شيء سليم، قم بتسجيل الدخول
            login(request, user)
            return JsonResponse({'success': True, 'redirect_url': '/accounts/dashboard/'})

        except User.DoesNotExist:
            # إذا لم يتم العثور على المستخدم من الأساس
            return JsonResponse({'success': False, 'message': 'اسم المستخدم أو كلمة المرور غير صحيحة.'})
        except Subscription.DoesNotExist:
             return JsonResponse({'success': False, 'message': 'لم يتم العثور على اشتراك لهذه الشركة.'})
            
    return render(request, 'accounts/login.html')


# --- دالة تسجيل حساب جديد (النسخة النهائية والمصححة) ---
def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
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

        company = Company.objects.create(name=company_name)
        Subscription.objects.create(company=company, is_active=False)
        CompanyProfile.objects.create(company=company)
        user = User.objects.create_user(username=username, password=password, company=company, is_active=False, is_staff=True)
        
        return JsonResponse({'success': True, 'message': 'تم إنشاء الحساب بنجاح! يرجى الآن تفعيل اشتراكك من صفحة الدخول.'})

    return render(request, 'accounts/register.html')

# --- لوحة التحكم (النسخة النهائية والمصححة) ---
# في ملف accounts/views.py

@login_required
def dashboard_view(request):
    # لا تغييرات على هذا الجزء
    if not request.user.company and not request.user.is_superuser:
        messages.error(request, _("حسابك غير مرتبط بأي شركة."))
        return redirect('logout')

    # المدير العام لا يحتاج لإكمال البيانات
    if request.user.is_superuser:
        context = {
            'company_name': "Superuser Dashboard",
            'today_date': date.today().strftime('%d/%m/%Y'),
            'subscription_days': "N/A",
            'show_profile_popup': False # المدير لا يرى النافذة
        }
        return render(request, 'accounts/dashboard_standalone.html', context)


    # --- المنطق الجديد للتحقق من ملف الشركة ---
    company = request.user.company
    subscription = None
    profile = None
    show_popup = False

    try:
        subscription = Subscription.objects.get(company=company)
    except Subscription.DoesNotExist:
        pass

    try:
        # نبحث عن ملف الشركة، وإذا لم نجده ننشئه
        profile, created = CompanyProfile.objects.get_or_create(company=company)
        # إذا كان ملف الشركة غير مكتمل، نرسل إشارة لإظهار النافذة
        if not profile.has_completed_profile:
            show_popup = True
    except CompanyProfile.DoesNotExist:
        # في حالة عدم وجود ملف، يجب إظهار النافذة
        show_popup = True
    
    context = {
        'company_name': company.name,
        'today_date': date.today().strftime('%d/%m/%Y'),
        'subscription_days': subscription.remaining_days if subscription else 0,
        'show_profile_popup': show_popup, # المتغير الجديد للتحكم في النافذة
        'profile': profile # نرسل البروفايل للوصول إلى بياناته في النافذة
    }
    return render(request, 'accounts/dashboard_standalone.html', context)


# --- دالة تسجيل الخروج ---
def logout_view(request):
    logout(request)
    return redirect('login')


# --- دالة تفعيل الاشتراك (النسخة النهائية والمصححة) ---
def activate_account_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            serial_number = data.get('serial_number')
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'بيانات غير صالحة.'})

        try:
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

    return JsonResponse({'success': False, 'message': 'طلب غير صالح.'})

# --- الدوال المؤقتة للصفحات الأخرى ---
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
def items_page_view(request): return render(request, 'accounts/coming_soon.html', {'page_title': 'الأصناف'})
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

# --- دوال الإدارة للمدير العام ---
@user_passes_test(is_superuser)
def manage_users_view(request):
    users = User.objects.all().order_by('company__name')
    context = {'users_list': users} # تم تصحيح اسم المتغير
    return render(request, 'accounts/manage_users.html', context)

@user_passes_test(is_superuser)
def manage_subscriptions_view(request):
    subscriptions = Subscription.objects.all()
    context = {'subscriptions_list': subscriptions} # تم تصحيح اسم المتغير
    return render(request, 'accounts/manage_subscriptions.html', context)

# في نهاية ملف accounts/views.py

@login_required
def update_company_profile_view(request):
    if request.method == 'POST':
        try:
            profile = CompanyProfile.objects.get(company=request.user.company)
            data = json.loads(request.body)

            profile.classification = data.get('classification')
            profile.country = data.get('country')
            profile.language = data.get('language')
            profile.has_completed_profile = True # أهم خطوة لمنع ظهور النافذة مرة أخرى
            profile.save()

            return JsonResponse({'success': True, 'message': 'تم حفظ البيانات بنجاح! جاري تحديث الصفحة...'})
        except CompanyProfile.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'لم يتم العثور على ملف الشركة.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'حدث خطأ: {str(e)}'})

    return JsonResponse({'success': False, 'message': 'طلب غير صالح.'}, status=400)