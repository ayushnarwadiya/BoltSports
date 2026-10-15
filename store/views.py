from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .cart import Cart
from .forms import CheckoutForm, RegisterForm
from .models import Category, Order, OrderItem, Product, Sport

def home(request):
    featured = list(Product.objects.filter(is_available=True).select_related('sport', 'category')[:8])
    hero = Product.objects.filter(slug='badminton-racket-grip-tape-pack-of-3').first()
    if hero is None and featured:
        hero = featured[0]
    context = {
        'sports': Sport.objects.all(),
        'featured': featured,
        'hero': hero,
    }
    return render(request, 'store/home.html', context)

def about(request):
    return render(request, 'store/about.html', {'sports': Sport.objects.all()})


def product_list(request):
    products = Product.objects.filter(is_available=True).select_related('sport', 'category')

    sport_slug = request.GET.get('sport', '')
    category_slug = request.GET.get('category', '')
    query = request.GET.get('q', '').strip()
    sort = request.GET.get('sort', 'newest')

    if sport_slug:
        products = products.filter(sport__slug=sport_slug)
    if category_slug:
        products = products.filter(category__slug=category_slug)
    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))

    sort_options = {
        'newest': '-created_at',
        'price_low': 'price',
        'price_high': '-price',
        'name': 'name',
    }
    products = products.order_by(sort_options.get(sort, '-created_at'))

    page_obj = Paginator(products, 9).get_page(request.GET.get('page'))

    params = request.GET.copy()
    params.pop('page', None)

    context = {
        'page_obj': page_obj,
        'sports': Sport.objects.all(),
        'categories': Category.objects.all(),
        'selected_sport': sport_slug,
        'selected_category': category_slug,
        'query': query,
        'sort': sort,
        'querystring': params.urlencode(),
    }
    return render(request, 'store/product_list.html', context)


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_available=True)
    related = (Product.objects.filter(sport=product.sport, is_available=True)
               .exclude(pk=product.pk).select_related('sport')[:4])
    return render(request, 'store/product_detail.html', {'product': product, 'related': related})

def cart_detail(request):
    cart = Cart(request)
    return render(request, 'store/cart.html', {'items': list(cart), 'total': cart.get_total()})


@require_POST
def cart_add(request, product_id):
    product = get_object_or_404(Product, pk=product_id, is_available=True)
    try:
        quantity = max(1, int(request.POST.get('quantity', 1)))
    except ValueError:
        quantity = 1

    if not product.in_stock:
        messages.error(request, f'Sorry, {product.name} is out of stock.')
    else:
        Cart(request).add(product, quantity)
        messages.success(request, f'{product.name} added to your cart.')

    next_url = request.POST.get('next', '')
    if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
        return redirect(next_url)
    return redirect('cart')


@require_POST
def cart_update(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    try:
        quantity = int(request.POST.get('quantity', 1))
    except ValueError:
        quantity = 1
    Cart(request).set_quantity(product, quantity)
    messages.success(request, 'Cart updated.')
    return redirect('cart')


@require_POST
def cart_remove(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    Cart(request).remove(product)
    messages.info(request, f'{product.name} removed from your cart.')
    return redirect('cart')

@login_required
def checkout(request):
    cart = Cart(request)
    if len(cart) == 0:
        messages.info(request, 'Your cart is empty.')
        return redirect('product_list')

    form = CheckoutForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        try:
            with transaction.atomic():
                order = form.save(commit=False)
                order.user = request.user
                order.save()

                total = 0
                for item in cart:
                    product = Product.objects.select_for_update().get(pk=item['product'].pk)
                    if item['quantity'] > product.stock:
                        raise ValueError(f'Only {product.stock} left of {product.name}.')
                    product.stock -= item['quantity']
                    product.save(update_fields=['stock'])
                    OrderItem.objects.create(order=order, product=product,
                                             quantity=item['quantity'], price=product.price)
                    total += product.price * item['quantity']

                order.total = total
                order.save(update_fields=['total'])
        except ValueError as error:
            messages.error(request, str(error))
            return redirect('cart')

        cart.clear()
        messages.success(request, 'Your order has been placed successfully!')
        return redirect('order_success', order_id=order.id)

    return render(request, 'store/checkout.html',
                  {'form': form, 'items': list(cart), 'total': cart.get_total()})


@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    return render(request, 'store/order_success.html', {'order': order})


@login_required
def order_history(request):
    orders = request.user.orders.prefetch_related('items__product')
    return render(request, 'store/order_history.html', {'orders': orders})


@login_required
@require_POST
def order_cancel(request, order_id):
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    if order.can_cancel:
        order.status = 'cancelled'
        order.save()  # the model puts the items back into stock
        messages.info(request, f'Order #{order.id} has been cancelled.')
    else:
        messages.error(request, 'This order can no longer be cancelled.')
    return redirect('order_detail', order_id=order.id)


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    return render(request, 'store/order_detail.html', {'order': order})

def register(request):
    if request.user.is_authenticated:
        return redirect('home')
    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, f'Welcome, {user.username}! Your account has been created.')
        return redirect('home')
    return render(request, 'store/register.html', {'form': form})
