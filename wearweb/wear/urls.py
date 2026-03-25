from django.urls import path
from . import views


urlpatterns = [
    path('customer/', views.customerdashboardview, name='customer_dashboard'),
    path('seller/', views.sellerdashboardview, name='seller_dashboard'),
    path('seller/add-product/', views.seller_add_product, name='seller_add_product'),
    path('seller/delete-product/<int:pk>/', views.seller_delete_product, name='seller_delete_product'),
    path('admin/', views.admindashboardview, name='admin_dashboard'),
    path('products/', views.product_list, name='product_list'),
    path('products/<int:pk>/', views.product_detail, name='product_detail'),
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:pk>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:pk>/', views.update_cart, name='update_cart'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('order-success/<int:pk>/', views.order_success_view, name='order_success'),
]