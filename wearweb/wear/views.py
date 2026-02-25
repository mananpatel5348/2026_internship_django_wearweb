from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required(login_url='login')
def customerdashboardview(request):
    return render(request, 'wear/customer_dashboard.html')

@login_required(login_url='login')
def sellerdashboardview(request):
    return render(request, 'wear/seller_dashboard.html')

@login_required(login_url='login')
def admindashboardview(request):
    return render(request, 'wear/admin_dashboard.html')