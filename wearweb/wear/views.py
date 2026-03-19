from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .decorators import role_required
from .models import Product, Category, Cart, CartItem

@role_required(allowd_roles=['customer'])
def customerdashboardview(request):
    products = Product.objects.filter(is_available=True)
    categories = Category.objects.all()
    return render(request, 'wear/customer/customer_dashboard.html', {
        'products': products,
        'categories': categories
    })

@role_required(allowd_roles=['seller'])
def sellerdashboardview(request):
    return render(request, 'wear/seller/seller_dashboard.html')

@role_required(allowd_roles=['admin'])
def admindashboardview(request):
    return render(request, 'wear/admin/admin_dashboard.html')

def product_list(request):
    products = Product.objects.filter(is_available=True)
    categories = Category.objects.all()
    selected_category = request.GET.get('category', '')
    if selected_category:
        products = products.filter(category__slug=selected_category)
    return render(request, 'wear/product_list.html', {
        'products': products,
        'categories': categories,
        'selected_category': selected_category
    })

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    related = Product.objects.filter(
        category=product.category, is_available=True
    ).exclude(pk=pk)[:4]
    return render(request, 'wear/product_detail.html', {
        'product': product,
        'related': related
    })

@login_required(login_url='/core/login/')
def add_to_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not item_created:
        cart_item.quantity += 1
        cart_item.save()
    messages.success(request, f'"{product.name}" cart mein add ho gaya!')
    return redirect('cart')

@login_required(login_url='/core/login/')
def remove_from_cart(request, pk):
    cart = get_object_or_404(Cart, user=request.user)
    cart_item = get_object_or_404(CartItem, cart=cart, pk=pk)
    cart_item.delete()
    messages.success(request, 'Item cart se remove ho gaya!')
    return redirect('cart')

@login_required(login_url='/core/login/')
def update_cart(request, pk):
    cart = get_object_or_404(Cart, user=request.user)
    cart_item = get_object_or_404(CartItem, cart=cart, pk=pk)
    qty = int(request.POST.get('quantity', 1))
    if qty > 0:
        cart_item.quantity = qty
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('cart')

@login_required(login_url='/core/login/')
def cart_view(request):
    try:
        cart = Cart.objects.get(user=request.user)
        items = cart.items.all()
    except Cart.DoesNotExist:
        cart = None
        items = []
    return render(request, 'wear/cart.html', {
        'cart': cart,
        'items': items
    })