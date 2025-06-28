from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
import json
from datetime import date, timedelta

# (!!!) هذا هو سطر الـ import الوحيد والصحيح لكل الموديلات (!!!)
from .models import User, Subscription, SystemPage, CompanyProfile

# --- دالة تسجيل الدخول (النسخة النهائية والمصححة) ---


def login_view(request):
    error_message = None
    if request.method == 'POST':
        username_data = request.POST.get('username')
        password_data = request.POST.get('password')

        # (1) أولاً، نحاول العثور على المستخدم بالاسم
        try:
            user = User.objects.get(username=username_data)

            # (2) ثانياً، نتحقق من حالة الحساب (هل هو فعال؟)
            if not user.is_active:
                error_message = "هذا الحساب غير مفعل. يرجى التواصل مع مدير النظام لتفعيله."

            # (3) ثالثاً، إذا كان فعالاً، نتحقق من كلمة المرور
            elif not user.check_password(password_data):
                error_message = 'اسم المستخدم أو كلمة المرور غير صحيحة.'

            else:
                # (4) إذا كان فعالاً وكلمة المرور صحيحة، نتحقق من الاشتراك
                # ونسجل دخوله

                # نسمح للسوبر يوزر بالدخول دائماً
                if user.is_superuser:
                    login(request, user)
                    return redirect('dashboard')

                try:
                    subscription = user.subscription
                    if subscription.is_active and (subscription.end_date is None or subscription.end_date >= date.today()):
                        login(request, user)
                        return redirect('dashboard')
                    else:
                        error_message = "لقد انتهى اشتراكك. يرجى التواصل مع مدير النظام."
                except Subscription.DoesNotExist:
                    error_message = "لا يوجد اشتراك مرتبط بهذا الحساب."

        except User.DoesNotExist:
            # إذا لم يتم العثور على المستخدم من الأساس
            error_message = 'اسم المستخدم أو كلمة المرور غير صحيحة.'

    context = {'error_message': error_message}
    return render(request, 'login.html', context)


# --- دالة تسجيل حساب جديد ---


def register_view(request):
    error_message = None
    success_message = None
    if request.method == 'POST':
        username_data = request.POST.get('username')
        email_data = request.POST.get('email')
        password_data = request.POST.get('password')
        password2_data = request.POST.get('password2')
        if password_data != password2_data:
            error_message = 'كلمتا المرور غير متطابقتين.'
        elif User.objects.filter(username=username_data).exists():
            error_message = 'اسم المستخدم هذا مسجل بالفعل.'
        else:
            user = User.objects.create_user(
                username=username_data, email=email_data, password=password_data)
            user.is_active = False
            user.save()
            Subscription.objects.create(user=user, is_active=False)
            CompanyProfile.objects.create(
                user=user, company_name="", classification="other", country="")
            success_message = 'تم إنشاء حسابك بنجاح. يرجى التواصل مع مدير النظام لتفعيله.'
    context = {'error_message': error_message,
               'success_message': success_message}
    return render(request, 'register.html', context)

# --- دالة تفعيل الحساب ---


def activate_account_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        serial = data.get('serial')
        try:
            subscription = Subscription.objects.get(
                user__username=username, serial_number=serial)
            if subscription.is_active:
                return JsonResponse({'status': 'error', 'message': 'هذا الحساب مفعل بالفعل.'})
            subscription.is_active = True
            subscription.start_date = date.today()
            subscription.end_date = date.today() + timedelta(days=365)
            subscription.save()
            subscription.user.is_active = True
            subscription.user.save()
            return JsonResponse({'status': 'success', 'message': 'تم تفعيل حسابك بنجاح! يمكنك الآن تسجيل الدخول.'})
        except Subscription.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'اسم المستخدم أو السيريال نمبر غير صحيح.'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})

# --- دالة تسجيل الخروج ---


def logout_view(request):
    logout(request)
    return redirect('login')

# --- الصفحات الداخلية المحمية ---

@login_required
def dashboard_view(request):
    user = request.user
    company_name_display = "اسم الشركة"
    subscription_days_left = 0
    show_profile_popup = False # سنستخدم هذا لاحقاً للنافذة المنبثقة

    # --- جلب بيانات ملف الشركة ---
    # get_or_create تبحث عن الملف، إذا لم تجده تقوم بإنشائه
    company_profile, created = CompanyProfile.objects.get_or_create(user=user)
    
    # إذا كان المستخدم لم يكمل بياناته، سنطلب منه ذلك لاحقاً
    if not company_profile.has_completed_profile:
        show_profile_popup = True
    
    # إذا كان لديه اسم شركة مسجل، نعرضه
    if company_profile.company_name:
        company_name_display = company_profile.company_name

    # --- جلب بيانات الاشتراك ---
    try:
        subscription = user.subscription
        if subscription.is_active and subscription.end_date:
            days_left = (subscription.end_date - date.today()).days
            subscription_days_left = max(0, days_left) # لعرض 0 بدلاً من رقم سالب
    except Subscription.DoesNotExist:
        subscription_days_left = 0 # إذا لم يكن له اشتراك

    # --- تجهيز كل البيانات لإرسالها للواجهة ---
    context = {
        'company_name': company_name_display,
        'today_date': date.today().strftime('%d/%m/%Y'),
        'subscription_days': subscription_days_left,
        'show_profile_popup': show_profile_popup,
    }
    return render(request, 'dashboard_standalone.html', context)


@login_required
def update_company_profile_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            profile = request.user.company_profile
            profile.company_name = data.get('company_name')
            profile.classification = data.get('classification')
            profile.country = data.get('country')
            profile.language = data.get('language')
            profile.has_completed_profile = True
            profile.save()
            return JsonResponse({'status': 'success', 'message': 'تم حفظ البيانات بنجاح!'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'طلب غير صالح'})


@login_required
def manage_users_view(request):
    if not request.user.groups.filter(name='مدراء النظام').exists():
        raise PermissionDenied
    all_users = User.objects.all().order_by('username')
    return render(request, 'manage_users.html', {'users_list': all_users})


@login_required
def edit_user_permissions_view(request, user_id):
    if not request.user.groups.filter(name='مدراء النظام').exists():
        raise PermissionDenied
    user_to_edit = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        user_to_edit.direct_permissions.set(request.POST.getlist('pages'))
        return redirect('manage_users')
    top_level_pages = SystemPage.objects.filter(parent__isnull=True)
    context = {'user_to_edit': user_to_edit,
               'top_level_pages': top_level_pages}
    return render(request, 'edit_permissions.html', context)

# --- دوال مؤقتة لصفحات الشريط الجانبي ---


@login_required
def sales_page_view(request):
    return render(request, 'coming_soon.html', {'page_title': 'المبيعات'})


@login_required
def clients_page_view(request):
    return render(request, 'coming_soon.html', {'page_title': 'العملاء'})


@login_required
def quotes_page_view(request):
    return render(request, 'coming_soon.html', {'page_title': 'عروض الأسعار'})


@login_required
def logistics_page_view(request):
    return render(request, 'coming_soon.html', {'page_title': 'المناديب والمخازن'})


@login_required
def purchases_page_view(request):
    return render(request, 'coming_soon.html', {'page_title': 'المشتريات'})


@login_required
def items_page_view(request):
    return render(request, 'coming_soon.html', {'page_title': 'الأصناف'})


@login_required
def upload_excel_page_view(request):
    return render(request, 'coming_soon.html', {'page_title': 'رفع ملف إكسل'})


@login_required
def transactions_page_view(request):
    return render(request, 'coming_soon.html', {'page_title': 'مصروفات وإيرادات'})


@login_required
def messages_page_view(request):
    return render(request, 'coming_soon.html', {'page_title': 'الرسائل'})


@login_required
def hr_page_view(request):
    return render(request, 'coming_soon.html', {'page_title': 'الموظفين والرواتب'})


@login_required
def reports_page_view(request):
    return render(request, 'coming_soon.html', {'page_title': 'التقارير'})


@login_required
def pos_page_view(request):
    return render(request, 'coming_soon.html', {'page_title': 'الخزن / نقاط البيع'})


@login_required
def settings_page_view(request):
    return render(request, 'coming_soon.html', {'page_title': 'الإعدادات'})

# --- دوال إدارة الاشتراكات ---


@login_required
def manage_subscriptions_view(request):
    # حماية الصفحة: لا يدخلها إلا مدير النظام
    if not request.user.groups.filter(name='مدراء النظام').exists():
        raise PermissionDenied

    # جلب كل الاشتراكات لعرضها
    all_subscriptions = Subscription.objects.all().select_related('user')

    context = {
        'subscriptions_list': all_subscriptions
    }
    return render(request, 'manage_subscriptions.html', context)


@login_required
def activate_subscription_view(request, sub_id):
    # حماية الصفحة
    if not request.user.groups.filter(name='مدراء النظام').exists():
        raise PermissionDenied

    # عند الضغط على زر التفعيل، سيتم إرسال طلب POST
    if request.method == 'POST':
        subscription_to_activate = get_object_or_404(Subscription, id=sub_id)

        # نقوم بتفعيل الاشتراك وتحديد مدته
        subscription_to_activate.is_active = True
        subscription_to_activate.start_date = date.today()
        subscription_to_activate.end_date = date.today() + timedelta(days=365)
        subscription_to_activate.save()

        # نقوم بتفعيل حساب المستخدم نفسه
        user_to_activate = subscription_to_activate.user
        user_to_activate.is_active = True
        user_to_activate.save()

    # في النهاية، نعود لنفس صفحة إدارة الاشتراكات
    return redirect('manage_subscriptions')


@login_required
def update_company_profile_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            profile, created = CompanyProfile.objects.get_or_create(
                user=request.user)

            profile.company_name = data.get('company_name')
            profile.classification = data.get('classification')
            profile.country = data.get('country')
            profile.language = data.get('language')
            profile.has_completed_profile = True  # <-- أهم خطوة لمنع ظهور النافذة مرة أخرى
            profile.save()

            return JsonResponse({'status': 'success', 'message': 'تم حفظ البيانات بنجاح! سيتم تحديث الصفحة.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'طلب غير صالح'})


@login_required
def update_company_profile_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            profile = request.user.company_profile

            profile.company_name = data.get('company_name', '')
            profile.classification = data.get('classification', '')
            profile.country = data.get('country', '')
            profile.language = data.get('language', 'ar')
            profile.has_completed_profile = True  # <-- أهم خطوة لمنع ظهور النافذة مرة أخرى
            profile.save()

            return JsonResponse({'status': 'success', 'message': 'تم حفظ البيانات بنجاح!'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'طلب غير صالح'})
