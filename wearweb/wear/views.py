from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .decorators import role_required
from .models import Product, Category, Cart, CartItem, Order, OrderItem, Address, Review, ReturnRequest


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

    # Search
    search_query = request.GET.get('search', '')
    if search_query:
        products = products.filter(name__icontains=search_query)

    # Category filter
    selected_category = request.GET.get('category', '')
    if selected_category:
        products = products.filter(category__slug=selected_category)

    # Price filter
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)

    # Sort
    sort = request.GET.get('sort', '')
    if sort == 'price_low':
        products = products.order_by('price')
    elif sort == 'price_high':
        products = products.order_by('-price')
    elif sort == 'newest':
        products = products.order_by('-created_at')

    return render(request, 'wear/product_list.html', {
        'products': products,
        'categories': categories,
        'selected_category': selected_category,
        'search_query': search_query,
        'min_price': min_price,
        'max_price': max_price,
        'sort': sort,
    })

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    related = Product.objects.filter(
        category=product.category, is_available=True
    ).exclude(pk=pk)[:4]
    reviews = product.reviews.all().order_by('-created_at')
    avg_rating = round(sum(r.rating for r in reviews) / reviews.count(), 1) if reviews.count() > 0 else 0
    user_reviewed = False
    if request.user.is_authenticated:
        user_reviewed = reviews.filter(user=request.user).exists()

    if request.method == 'POST' and request.user.is_authenticated:
        if not user_reviewed:
            rating = int(request.POST.get('rating', 5))
            comment = request.POST.get('comment', '')
            if comment:
                Review.objects.create(
                    product=product,
                    user=request.user,
                    rating=rating,
                    comment=comment
                )
                messages.success(request, 'Review submit ho gaya! ⭐')
                return redirect(f'/wear/products/{pk}/')

    return render(request, 'wear/product_detail.html', {
        'product': product,
        'related': related,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'user_reviewed': user_reviewed,
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

    return render(request, 'wear/checkout.html', {
        'cart': cart,
        'items': items,
    })


@login_required(login_url='/core/login/')
def payment_view(request):
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
        # Session mein address save karo
        request.session['address_id'] = address.pk
        request.session['payment_method'] = request.POST.get('payment')
        return redirect('payment_page')

    return redirect('checkout')


@login_required(login_url='/core/login/')
def payment_page(request):
    try:
        cart = Cart.objects.get(user=request.user)
        items = cart.items.all()
    except Cart.DoesNotExist:
        return redirect('cart')

    total = cart.get_total()
    payment_method = request.session.get('payment_method', 'cod')

    return render(request, 'wear/payment.html', {
        'cart': cart,
        'items': items,
        'total': total,
        'payment_method': payment_method,
    })


@login_required(login_url='/core/login/')
def process_payment(request):
    if request.method == 'POST':
        try:
            cart = Cart.objects.get(user=request.user)
            items = cart.items.all()
        except Cart.DoesNotExist:
            return redirect('cart')

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

        # Session clear karo
        request.session.pop('address_id', None)
        request.session.pop('payment_method', None)

        return redirect(f'/wear/order-success/{order.pk}/')

    return redirect('cart')


@login_required(login_url='/core/login/')
def order_success_view(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    return render(request, 'wear/order_success.html', {'order': order})

@login_required(login_url='/core/login/')
def order_tracking(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    return render(request, 'wear/order_tracking.html', {'order': order})

@login_required(login_url='/core/login/')
def return_request_view(request, order_pk):
    order = get_object_or_404(Order, pk=order_pk, user=request.user)

    # Sirf delivered orders pe return allowed
    if order.status != 'delivered':
        messages.error(request, 'Sirf delivered orders pe return request kar sakte ho!')
        return redirect('order_tracking', pk=order_pk)

    # Check already requested
    already_requested = ReturnRequest.objects.filter(order=order, user=request.user).exists()
    if already_requested:
        messages.error(request, 'Is order ke liye pehle se return request hai!')
        return redirect('order_tracking', pk=order_pk)

    if request.method == 'POST':
        reason = request.POST.get('reason')
        description = request.POST.get('description')
        ReturnRequest.objects.create(
            order=order,
            user=request.user,
            reason=reason,
            description=description,
        )
        messages.success(request, 'Return request successfully submit ho gayi!')
        return redirect('my_returns')

    return render(request, 'wear/return_request.html', {'order': order})


@login_required(login_url='/core/login/')
def my_returns_view(request):
    returns = ReturnRequest.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'wear/my_returns.html', {'returns': returns})

def delivery_info(request):
    return render(request, 'wear/delivery_info.html')

def payment_info(request):
    return render(request, 'wear/payment_info.html')

def return_policy(request):
    return render(request, 'wear/return_policy.html')