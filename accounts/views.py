from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied
from .models import User, Subscription
from datetime import date
from django.http import JsonResponse
import json
from datetime import date, timedelta

# --- دالة تسجيل الدخول ---


def login_view(request):
    error_message = None
    if request.method == 'POST':
        username_data = request.POST.get('username')
        password_data = request.POST.get('password')
        try:
            user_obj = User.objects.get(username=username_data)
            if user_obj.check_password(password_data):
                if user_obj.is_active:
                    try:
                        subscription = user_obj.subscription
                        if subscription.is_active and (subscription.end_date is None or subscription.end_date >= date.today()):
                            login(request, user_obj)
                            return redirect('dashboard')
                        else:
                            error_message = "لقد انتهى اشتراكك. يرجى التواصل مع مدير النظام لتجديده."
                    except Subscription.DoesNotExist:
                        error_message = "لا يوجد اشتراك مرتبط بهذا الحساب. يرجى التواصل مع مدير النظام."
                else:
                    error_message = "هذا الحساب غير مفعل. يرجى التواصل مع مدير النظام لتفعيله."
            else:
                error_message = 'اسم المستخدم أو كلمة المرور غير صحيحة.'
        except User.DoesNotExist:
            error_message = 'اسم المستخدم أو كلمة المرور غير صحيحة.'
    context = {'error_message': error_message}
    return render(request, 'login.html', context)

# --- دالة لوحة التحكم ---


@login_required
def dashboard_view(request):
    user = request.user
    subscription_days_left = 0
    try:
        subscription = user.subscription
        if subscription.is_active and subscription.end_date:
            days_left = (subscription.end_date - date.today()).days
            subscription_days_left = max(0, days_left)
    except Subscription.DoesNotExist:
        subscription_days_left = 0
    context = {
        'company_name': 'شركة MIA للأثاث المودرن',
        'today_date': date.today().strftime('%d/%m/%Y'),
        'subscription_days': subscription_days_left,
    }
    return render(request, 'dashboard.html', context)

# --- دالة تسجيل الخروج ---


def logout_view(request):
    logout(request)
    return redirect('login')

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
        elif User.objects.filter(email=email_data).exists():
            error_message = 'هذا البريد الإلكتروني مسجل بالفعل.'
        else:
            user = User.objects.create_user(
                username=username_data, email=email_data, password=password_data)
            user.is_active = False
            user.save()
            Subscription.objects.create(user=user, is_active=False)
            success_message = 'تم إنشاء حسابك بنجاح. يرجى التواصل مع مدير النظام لتفعيله.'
    context = {'error_message': error_message,
               'success_message': success_message}
    return render(request, 'register.html', context)

# --- دالة إدارة المستخدمين ---


@login_required
def manage_users_view(request):
    if not request.user.groups.filter(name='مدراء النظام').exists():
        raise PermissionDenied
    all_users = User.objects.all().order_by('username')
    context = {
        'users_list': all_users
    }
    return render(request, 'manage_users.html', context)

# --- دالة تعديل صلاحيات المستخدم ---


@login_required
def edit_user_permissions_view(request, user_id):
    if not request.user.groups.filter(name='مدراء النظام').exists():
        raise PermissionDenied

    user_to_edit = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        # عند الحفظ، نحصل على كل أرقام الصلاحيات التي تم تحديدها
        selected_pages_ids = request.POST.getlist('pages')
        # نقوم بحفظ هذه الصلاحيات مباشرة للمستخدم
        user_to_edit.direct_permissions.set(selected_pages_ids)
        return redirect('manage_users')

    # نحضر فقط الصلاحيات "الأب" (التي ليس لها أب) لعرضها
    top_level_pages = SystemPage.objects.filter(parent__isnull=True)

    context = {
        'user_to_edit': user_to_edit,
        'top_level_pages': top_level_pages,
    }
    return render(request, 'edit_permissions.html', context)

def activate_account_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        serial = data.get('serial')

        try:
            # نبحث عن الاشتراك المطابق للسيريال واسم المستخدم
            subscription = Subscription.objects.get(
                user__username=username, 
                serial_number=serial
            )

            # نتأكد أن الاشتراك ليس فعالاً بالفعل
            if subscription.is_active:
                return JsonResponse({'status': 'error', 'message': 'هذا الحساب مفعل بالفعل.'})

            # كل شيء صحيح، نقوم بالتفعيل
            subscription.is_active = True
            subscription.start_date = date.today()
            subscription.end_date = date.today() + timedelta(days=365)
            subscription.save()

            # نقوم بتفعيل حساب المستخدم أيضاً
            subscription.user.is_active = True
            subscription.user.save()

            return JsonResponse({'status': 'success', 'message': 'تم تفعيل حسابك بنجاح! يمكنك الآن تسجيل الدخول.'})

        except Subscription.DoesNotExist:
            # إذا لم يتم العثور على اشتراك مطابق
            return JsonResponse({'status': 'error', 'message': 'اسم المستخدم أو السيريال نمبر غير صحيح.'})

    # إذا كان الطلب ليس POST، نرجع خطأ
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})