from django.urls import path
from . import views

urlpatterns = [
    # --- روابط الحسابات الأساسية ---
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('activate-account/', views.activate_account_view, name='activate_account'),

    # --- رابط لوحة التحكم ---
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    # --- رابط تحديث ملف الشركة ---
    path('update-profile/', views.update_company_profile_view, name='update_profile'),

    # --- روابط إدارة الموظفين ---
    path('manage-employees/', views.manage_employees_view, name='manage_employees'),
    path('add-employee/', views.add_employee_view, name='add_employee'),
    path('employee/<int:employee_id>/permissions/', views.edit_employee_permissions_view, name='edit_employee_permissions'),
    path('employee/<int:employee_id>/permissions/save/', views.save_employee_permissions_view, name='save_employee_permissions'),
    path('employee/<int:employee_id>/delete/', views.delete_employee_view, name='delete_employee'),
    # --- روابط الإدارة للمدير العام ---
    path('manage-users/', views.manage_users_view, name='manage_users'),
    path('manage-subscriptions/', views.manage_subscriptions_view, name='manage_subscriptions'),

    # --- روابط الصفحات المؤقتة ---
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
    path('add-item/', views.add_item_view, name='add_item'),
    path('item/<int:item_id>/delete/', views.delete_item_view, name='delete_item'),
    path('item/<int:item_id>/edit/', views.edit_item_view, name='edit_item'), 
    path('inventory/', views.inventory_page_view, name='inventory_page'),
    path('new-sale/', views.new_sale_view, name='new_sale'),
    path('journal-entry/', views.journal_entry_view, name='journal_entry'),
    path('chart-of-accounts/', views.chart_of_accounts_view, name='chart_of_accounts'),
    path('cashboxes/', views.cashbox_management_view, name='cashbox_management'),
    path('cashbox-transaction/new/', views.new_cashbox_transaction_view, name='new_cashbox_transaction'),
    path('cashbox-report/', views.cashbox_report_view, name='cashbox_report'),
    path('clients/manage/', views.client_management_view, name='client_management'),
    path('settings-dashboard/', views.settings_dashboard_view, name='settings_dashboard'),
]