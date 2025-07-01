from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from accounts.decorators import company_required, subscription_required, page_permission_required

# ... (الكود الموجود بالفعل) ...

# أضف هذه الدالة الجديدة في نهاية الملف
@login_required
@company_required
@subscription_required
@page_permission_required("items")
def items_page(request):
    """
    View لعرض صفحة إدارة الأصناف.
    """
    # حالياً سنعرض الصفحة فقط، لاحقاً سنضيف منطق عرض الأصناف من قاعدة البيانات
    context = {
        'page_name': 'items',
    }
    return render(request, "operations/items.html", context)