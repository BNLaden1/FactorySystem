# operations/urls.py
from django.urls import path
from . import views

app_name = 'operations'

urlpatterns = [
    # 1. صفحة عرض كل المشاريع
    path('projects/', views.project_list_view, name='project-list'),

    # 2. صفحة إضافة مشروع واحد
    path('projects/add/', views.add_project_view, name='project-add'),

    # 3. صفحة الإضافة المجمعة
    path('projects/add-bulk/', views.bulk_add_projects_view, name='project-add-bulk'),

    # 4. صفحة تفاصيل المشروع
    path('project/<int:project_id>/', views.project_detail_view, name='project-detail'),

    # 5. رابط تغيير حالة المشروع
    path('project/<int:project_id>/set-status/', views.set_project_status_view, name='project-set-status'),

    # 6. ▼▼▼ هذا هو الرابط الذي كان ناقصاً ▼▼▼
    path('cost-types/', views.manage_cost_types_view, name='cost-type-manage'),
    path('cost-item/<int:item_id>/delete/', views.delete_cost_item_view, name='cost-item-delete'),
    path('payment/<int:payment_id>/delete/', views.delete_payment_view, name='payment-delete'),
    path('payment/<int:payment_id>/edit/', views.edit_payment_view, name='payment-edit'),
]
