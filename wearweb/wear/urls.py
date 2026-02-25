from django.urls import path
from . import views
urlpatterns = [
    path('customer/', views.customerdashboardview, name='customer_dashboard'),
    path('seller/', views.sellerdashboardview, name='seller_dashboard'),
    path('admin/', views.admindashboardview, name='admin_dashboard')
]