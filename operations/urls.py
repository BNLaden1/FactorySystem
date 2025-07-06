# operations/urls.py
from django.urls import path
from . import views

app_name = 'operations'

urlpatterns = [
    # الرابط الأول: صفحة عرض كل المشاريع
    path('projects/', views.project_list_view, name='project-list'),

    # الرابط الثاني: صفحة إضافة مشروع واحد
    path('projects/add/', views.add_project_view, name='project-add'),

    # الرابط الثالث: صفحة الإضافة المجمعة
    path('projects/add-bulk/', views.bulk_add_projects_view, name='project-add-bulk'),

    # ▼▼▼ هذا هو الرابط الجديد الذي ستضيفه لصفحة تفاصيل المشروع ▼▼▼
    path('project/<int:project_id>/', views.project_detail_view, name='project-detail'),
]