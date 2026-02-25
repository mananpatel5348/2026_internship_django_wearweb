from django.shortcuts import render

# Create your views here.
def customerdashboardview(request):
    return render(request, 'wear/customer_dashboard.html')

def sellerdashboardview(request):
    return render(request, 'wear/seller_dashboard.html')

def admindashboardview(request):
    return render(request, 'wear/admin_dashboard.html')