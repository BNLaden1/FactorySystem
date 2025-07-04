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
from django.contrib.auth import get_user_model
User = get_user_model()

# (!!!) تأكد من أن هذا السطر يستدعي كل الموديلات الصحيحة (!!!)
from .models import User, Company, Subscription, CompanyProfile, SystemPage, Item
from datetime import timedelta
from django.utils import timezone
from .models import IPRegistrationRecord, Group
from .decorators import page_permission_required 
from .models import ChartOfAccount, JournalEntry, Transaction, Cashbox, CashboxTransaction, Client, Supplier
from django.utils import timezone
from decimal import Decimal



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
@transaction.atomic # يضمن حفظ كل الأصناف معاً أو لا شيء
def add_item_view(request):
    if not request.user.company:
        return JsonResponse({'success': False, 'message': 'طلب غير مصرح به.'})

    if request.method == 'POST':
        try:
            items_data = json.loads(request.body)
            company = request.user.company
            
            items_to_create = []
            for item_data in items_data:
                if item_data.get('name'): # تجاهل الصفوف الفارغة
                    items_to_create.append(
                        Item(
                            company=company,
                            name=item_data.get('name'),
                            code=item_data.get('code'),
                            price=item_data.get('price', 0),
                            cost=item_data.get('cost', 0),
                            quantity=item_data.get('quantity', 0)
                        )
                    )
            
            # حفظ كل الأصناف في عملية واحدة سريعة
            if items_to_create:
                Item.objects.bulk_create(items_to_create)
                return JsonResponse({'success': True, 'message': 'تمت إضافة الأصناف بنجاح!'})
            else:
                return JsonResponse({'success': False, 'message': 'لم يتم إرسال أي بيانات صالحة.'}, status=400)

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
# accounts/views.py
from django.forms.models import model_to_dict
import json
# تأكد من استدعاء get_object_or_404 و transaction في بداية الملف
from django.shortcuts import get_object_or_404
from django.db import transaction

# ▼▼▼ قم بإضافة هاتين الدالتين في نهاية الملف ▼▼▼

@login_required
def edit_item_view(request, item_id):
    if request.method == 'POST':
        try:
            # نبحث عن الصنف ونتأكد أنه يخص شركة المستخدم
            item = get_object_or_404(Item, id=item_id, company=request.user.company)
            data = json.loads(request.body)

            # تحديث بيانات الصنف بالبيانات الجديدة
            item.name = data.get('name', item.name)
            item.code = data.get('code', item.code)
            item.price = data.get('price', item.price)
            item.quantity = data.get('quantity', item.quantity)
            item.save() # حفظ التغييرات

            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=400)
    
    return JsonResponse({'success': False, 'message': 'طلب غير صالح.'}, status=400)

@login_required
def get_item_details_view(request, item_id):
    try:
        item = get_object_or_404(Item, id=item_id, company=request.user.company)
        # نحول بيانات الصنف إلى قاموس (dictionary) لنرسله كـ JSON
        item_data = model_to_dict(item)
        return JsonResponse({'success': True, 'item': item_data})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=404)

# ▲▲▲ نهاية الدوال الجديدة ▲▲▲
@login_required
@page_permission_required("inventory_page") 
def inventory_page_view(request):
    # جلب كل الأصناف الخاصة بالشركة الحالية
    items_list = Item.objects.filter(company=request.user.company)
    
    context = {
        'items_list': items_list,
        'page_name': 'inventory_page', # مهمة لتمييز الصفحة النشطة
    }
    return render(request, 'accounts/inventory.html', context)

# accounts/views.py

@login_required
@page_permission_required("new_sale")
def new_sale_view(request):
    company = request.user.company
    
    if request.method == 'POST':
        try:
            # استلام البيانات من الفورم
            item_id = request.POST.get('item_id')
            quantity_sold = Decimal(request.POST.get('quantity_sold', 0))
            cashbox_id = request.POST.get('cashbox_id')
            payment_method = request.POST.get('payment_method')

            with transaction.atomic():
                # جلب الصنف من قاعدة البيانات
                item_to_sell = Item.objects.select_for_update().get(id=item_id, company=company)

                # التحقق من توفر الكمية
                if item_to_sell.quantity < quantity_sold:
                    # يمكنك إضافة رسالة خطأ هنا
                    # messages.error(request, "الكمية المطلوبة غير متوفرة.")
                    return redirect('new_sale')
                
                # خصم الكمية من المخزون
                item_to_sell.quantity -= quantity_sold
                item_to_sell.save()

                # --- ✨ هذا هو الجزء الذي تم تصحيحه ---
                # حساب إجمالي الفاتورة مباشرةً
                total_amount = item_to_sell.price * quantity_sold

                # لو كان الدفع نقدي، قم بإنشاء حركة خزنة
                if payment_method == 'cash' and cashbox_id and total_amount > 0:
                    cashbox_instance = Cashbox.objects.select_for_update().get(id=cashbox_id, company=company)
                    
                    CashboxTransaction.objects.create(
                        company=company,
                        cashbox=cashbox_instance,
                        transaction_type='in',
                        amount=total_amount,
                        category='customer_payment',
                        description=f"تحصيل قيمة مبيعات الصنف: {item_to_sell.name}"
                    )
                    
                    # تحديث رصيد الخزنة
                    cashbox_instance.balance += total_amount
                    cashbox_instance.save()
                # --- نهاية الجزء المصحح ---

            # يمكنك إضافة رسالة نجاح هنا
            # messages.success(request, "تم حفظ الفاتورة بنجاح.")
            return redirect('inventory_page') # توجيه المستخدم لصفحة المخزون ليرى التغيير

        except Exception as e:
            # messages.error(request, f"حدث خطأ: {e}")
            return redirect('new_sale')

    # جلب البيانات لعرضها في الصفحة
    items = Item.objects.filter(company=company, quantity__gt=0)
    cashboxes = Cashbox.objects.filter(company=company, is_active=True)
    context = {
        'items_list': items,
        'page_name': 'new_sale',
        'cashboxes': cashboxes,
    }
    return render(request, 'accounts/new_sale.html', context)

@login_required
@page_permission_required("journal_entry")
def journal_entry_view(request):
    company = request.user.company
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            with transaction.atomic():
                # جلب الحساب الرئيسي (مصدر الأموال)
                main_account = ChartOfAccount.objects.get(id=data.get('main_account_id'), company=company)
                
                # إنشاء رأس القيد
                new_entry = JournalEntry.objects.create(
                    company=company,
                    date=data.get('date'),
                    description=data.get('description')
                )
                
                total_amount = 0
                transactions_to_create = []
                
                # إنشاء الحركات المدينة (التي أخذت الفلوس)
                for line in data.get('transactions', []):
                    amount = float(line.get('amount', 0))
                    if amount > 0:
                        sub_account = ChartOfAccount.objects.get(id=line.get('sub_account_id'), company=company)
                        transactions_to_create.append(
                            Transaction(journal_entry=new_entry, account=sub_account, debit=amount)
                        )
                        total_amount += amount
                
                # إنشاء الحركة الدائنة (مصدر الأموال)
                if total_amount > 0:
                    transactions_to_create.append(
                        Transaction(journal_entry=new_entry, account=main_account, credit=total_amount)
                    )
                
                # حفظ كل الحركات مرة واحدة
                Transaction.objects.bulk_create(transactions_to_create)

            return JsonResponse({'success': True, 'message': 'تم حفظ القيد بنجاح.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=400)

    # جلب البيانات لعرضها في الصفحة
    accounts = ChartOfAccount.objects.filter(company=company)
    recent_entries = JournalEntry.objects.filter(company=company).order_by('-date', '-id')[:10]
    
    context = {
        'accounts': accounts,
        'page_name': 'journal_entry',
        'today': timezone.now(),
        'recent_entries': recent_entries,
    }
    return render(request, 'accounts/journal_entry.html', context)


@login_required
@page_permission_required('chart_of_accounts') # تأكد من أن هذا الـ decorator موجود
def chart_of_accounts_view(request):
    # 1. نحصل على شركة المستخدم الحالي أولاً
    # هذا السطر هو أهم جزء في الحل
    company = request.user.company
    
    if request.method == 'POST':
        account_name = request.POST.get('account_name')
        account_type = request.POST.get('account_type')
        if account_name and account_type:
            # 2. عند إنشاء الحساب، نقوم بتمرير الشركة
            ChartOfAccount.objects.create(
                company=company, 
                name=account_name,
                account_type=account_type
            )
        return redirect('chart_of_accounts')

    # باقي الكود لجلب وعرض البيانات
    accounts = ChartOfAccount.objects.filter(company=company)
    account_types = ChartOfAccount.ACCOUNT_TYPE_CHOICES
    
    context = {
        'accounts': accounts,
        'account_types': account_types,
        'page_name': 'chart_of_accounts',
    }
    return render(request, 'accounts/chart_of_accounts.html', context)


@login_required
@page_permission_required("cashbox_management")
def cashbox_management_view(request):
    company = request.user.company
    
    if request.method == 'POST':
        name = request.POST.get('name')
        box_type = request.POST.get('box_type')
        initial_balance = request.POST.get('initial_balance', 0)

        if name and box_type:
            Cashbox.objects.create(
                company=company,
                name=name,
                box_type=box_type,
                balance=initial_balance
            )
        return redirect('cashbox_management')

    cashboxes = Cashbox.objects.filter(company=company)
    box_types = Cashbox.CASHBOX_TYPE_CHOICES
    
    context = {
        'cashboxes': cashboxes,
        'box_types': box_types,
        'page_name': 'cashbox_management',
    }
    return render(request, 'accounts/cashbox_management.html', context)

@login_required
@page_permission_required("new_cashbox_transaction")
def new_cashbox_transaction_view(request):
    company = request.user.company
    
    if request.method == 'POST':
        # سنقوم ببرمجة منطق الحفظ لاحقًا
        pass

    # --- ✨ بداية الكود الجديد والمُحسَّن لجلب البيانات ✨ ---
    
    # 1. جلب القوائم من قاعدة البيانات
    clients = list(Client.objects.filter(company=company).values('id', 'name'))
    suppliers = list(Supplier.objects.filter(company=company).values('id', 'name'))
    employees = list(User.objects.filter(company=company, is_staff=True).exclude(is_superuser=True).values('id', 'username'))
    # نفترض أن المصروفات موجودة في دليل الحسابات
    expenses = list(ChartOfAccount.objects.filter(company=company, account_type='Expense').values('id', 'name'))

    # 2. تجميع كل البيانات في قاموس واحد
    sub_account_data = {
        'client': clients,
        'supplier': suppliers,
        'employee': employees,
        'expense': expenses,
    }

    context = {
        'cashboxes': Cashbox.objects.filter(company=company, is_active=True),
        'categories': CashboxTransaction.CATEGORY_CHOICES,
        'page_name': 'new_cashbox_transaction',
        'today': timezone.now(),
        # ✨ 3. نرسل البيانات كـ JSON string آمن للواجهة
        'sub_account_json': json.dumps(sub_account_data)
    }
    return render(request, 'accounts/new_cashbox_transaction.html', context)


@login_required
@page_permission_required("cashbox_report")
def cashbox_report_view(request):
    company = request.user.company
    
    # جلب الخزن لعرضها في الفلتر
    cashboxes = Cashbox.objects.filter(company=company)
    
    # استلام بيانات الفلتر من المستخدم
    selected_cashbox_id = request.GET.get('cashbox')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    transactions = CashboxTransaction.objects.filter(company=company)

    if selected_cashbox_id:
        transactions = transactions.filter(cashbox_id=selected_cashbox_id)
    
    if start_date:
        transactions = transactions.filter(date__gte=start_date)

    if end_date:
        transactions = transactions.filter(date__lte=end_date)

    context = {
        'cashboxes': cashboxes,
        'transactions': transactions,
        'selected_cashbox_id': selected_cashbox_id,
        'start_date': start_date,
        'end_date': end_date,
        'page_name': 'cashbox_report',
    }
    return render(request, 'accounts/cashbox_report.html', context)

@login_required
@page_permission_required("client_management")
def client_management_view(request):
    company = request.user.company
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        if name:
            Client.objects.create(
                company=company,
                name=name,
                phone=phone,
                address=address
            )
        return redirect('client_management')

    clients = Client.objects.filter(company=company)
    context = {
        'clients': clients,
        'page_name': 'client_management',
    }
    return render(request, 'accounts/client_management.html', context)
@login_required
@page_permission_required("settings_dashboard")
def settings_dashboard_view(request):
    context = {
        'page_name': 'settings_dashboard',
    }
    return render(request, 'accounts/settings_dashboard.html', context)