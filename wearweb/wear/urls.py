from django.urls import path
from . import views
urlpatterns = [
    path('customer/', views.customerdashboardview, name='customer_dashboard'),
    path('seller/', views.sellerdashboardview, name='seller_dashboard'),
    path('admin/', views.admindashboardview, name='admin_dashboard'),
    path('products/', views.product_list, name='product_list'),
    path('products/<int:pk>/', views.product_detail, name='product_detail'),
    path('cart', views.cart_view, name='cart'),
    path('add-to-cart/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:pk>/', views.remove_from_cart, name='remove_from_cart'),
    path('update-cart/<int:pk>/', views.update_cart, name='update_cart'),   
]