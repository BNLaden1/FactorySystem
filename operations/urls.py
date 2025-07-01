from django.urls import path
from . import views

urlpatterns = [
    # الرابط القديم الخاص بالصفحة الرئيسية للعمليات
    path('', views.operations_home, name='operations_home'),

    # <<< أضف هذا السطر الجديد لربط صفحة الأصناف
    path('items/', views.items_page, name='items'),
]