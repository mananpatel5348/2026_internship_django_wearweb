from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .decorators import role_required
from .models import Product, Category, Cart, CartItem
from .models import Product, Category, Cart, CartItem, Order, OrderItem, Address

@role_required(allowd_roles=['customer'])
def customerdashboardview(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    cart_count = 0
    try:
        cart = Cart.objects.get(user=request.user)
        cart_count = cart.items.count()
    except Cart.DoesNotExist:
        pass
    return render(request, 'wear/customer/customer_dashboard.html', {
        'orders': orders,
        'cart_count': cart_count,
    })

@role_required(allowd_roles=['seller'])
def sellerdashboardview(request):
    products = Product.objects.filter(seller=request.user)
    total_orders = OrderItem.objects.filter(product__seller=request.user).count()
    total_revenue = sum(
        item.get_subtotal() 
        for item in OrderItem.objects.filter(product__seller=request.user)
    )
    return render(request, 'wear/seller/seller_dashboard.html', {
        'products': products,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
    })


@role_required(allowd_roles=['seller'])
def seller_add_product(request):
    categories = Category.objects.all()
    if request.method == 'POST':
        Product.objects.create(
            seller=request.user,
            name=request.POST.get('name'),
            description=request.POST.get('description'),
            price=request.POST.get('price'),
            discount_price=request.POST.get('discount_price') or None,
            category=Category.objects.get(pk=request.POST.get('category')),
            stock=request.POST.get('stock'),
            image=request.FILES.get('image'),
            is_available=True,
        )
        messages.success(request, 'Product successfully add ho gaya!')
        return redirect('seller_dashboard')
    return render(request, 'wear/seller/add_product.html', {'categories': categories})


@role_required(allowd_roles=['seller'])
def seller_delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk, seller=request.user)
    product.delete()
    messages.success(request, 'Product delete ho gaya!')
    return redirect('seller_dashboard')

@role_required(allowd_roles=['admin'])
def admindashboardview(request):
    from core.models import User
    total_users = User.objects.count()
    total_products = Product.objects.count()
    total_orders = Order.objects.count()
    total_revenue = sum(o.total_amount for o in Order.objects.all())
    recent_orders = Order.objects.order_by('-created_at')[:10]
    all_products = Product.objects.all().order_by('-id')[:8]
    return render(request, 'wear/admin/admin_dashboard.html', {
        'total_users': total_users,
        'total_products': total_products,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'recent_orders': recent_orders,
        'all_products': all_products,
    })

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

@login_required(login_url='/core/login/')
def checkout_view(request):
    try:
        cart = Cart.objects.get(user=request.user)
        items = cart.items.all()
    except Cart.DoesNotExist:
        return redirect('product_list')

    if not items:
        return redirect('cart')

    if request.method == 'POST':
        # Address save karo
        address = Address.objects.create(
            user=request.user,
            full_name=request.POST.get('full_name'),
            phone=request.POST.get('phone'),
            address_line=request.POST.get('address_line'),
            city=request.POST.get('city'),
            state=request.POST.get('state'),
            pincode=request.POST.get('pincode'),
        )

        # Order banao
        order = Order.objects.create(
            user=request.user,
            total_amount=cart.get_total(),
            status='confirmed'
        )

        # Order items banao
        for item in items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.discount_price or item.product.price
            )

        # Cart clear karo
        items.delete()

        return redirect(f'/wear/order-success/{order.pk}/')

    return render(request, 'wear/checkout.html', {
        'cart': cart,
        'items': items,
    })


@login_required(login_url='/core/login/')
def order_success_view(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    return render(request, 'wear/order_success.html', {'order': order})
