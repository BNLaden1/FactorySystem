"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from . import views

# هذه القائمة الآن تحتوي على رابط لكل أيقونة في الشريط الجانبي
urlpatterns = [
    # --- روابط الحسابات الأساسية ---
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('activate-account/', views.activate_account_view, name='activate_account'),

    # --- رابط الصفحة الرئيسية ---
    path('dashboard/', views.dashboard_view, name='dashboard'),

    # --- روابط الصفحات المؤقتة (قيد الإنشاء) ---
    path('sales/', views.sales_page_view, name='sales_page'),
    path('clients/', views.clients_page_view, name='clients_page'),
    path('quotes/', views.quotes_page_view, name='quotes_page'),
    path('logistics/', views.logistics_page_view, name='logistics_page'),
    path('purchases/', views.purchases_page_view, name='purchases_page'),
    path('items/', views.items_page_view, name='items_page'),
    path('upload-excel/', views.upload_excel_page_view, name='upload_excel_page'),
    path('transactions/', views.transactions_page_view, name='transactions_page'),
    path('messages/', views.messages_page_view, name='messages_page'),
    path('hr/', views.hr_page_view, name='hr_page'),
    path('reports/', views.reports_page_view, name='reports_page'),
    path('pos/', views.pos_page_view, name='pos_page'),
    path('settings/', views.settings_page_view, name='settings_page'),

    # --- روابط إدارة النظام (للمدير العام) ---
    path('manage-users/', views.manage_users_view, name='manage_users'),
    path('manage-subscriptions/', views.manage_subscriptions_view, name='manage_subscriptions'),
    
    # تم تعطيل الروابط التالية مؤقتاً لأن الدوال الخاصة بها لم نقم ببنائها بعد في ملف views.py الجديد
    # path('user/<int:user_id>/edit-permissions/',
    #      views.edit_user_permissions_view, name='edit_user_permissions'),
    # path('update-profile/', views.update_company_profile_view,
    #      name='update_profile'),
    # path('subscription/<int:sub_id>/activate/',
    #      views.activate_subscription_view, name='activate_subscription'),
]