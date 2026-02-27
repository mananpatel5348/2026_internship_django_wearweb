from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .decorators import role_required

# Create your views here.
#@login_required(login_url='login')
@role_required(allowd_roles=['customer'])
def customerdashboardview(request):
    return render(request, 'wear/customer/customer_dashboard.html')

#@login_required(login_url='login')
@role_required(allowd_roles=['seller'])
def sellerdashboardview(request):
    return render(request, 'wear/seller/seller_dashboard.html')

#@login_required(login_url='login')
@role_required(allowd_roles=['admin'])
def admindashboardview(request):
    return render(request, 'wear/admin/admin_dashboard.html')