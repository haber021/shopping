from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseRedirect, JsonResponse
from django.views.decorators.http import require_POST
from django.urls import reverse
from django.conf import settings
from django.utils import timezone

from .models import (
    Category, Product, Customer, Order, OrderItem, 
    InventoryTransaction, DeliveryLocation, OrderStatusHistory,
    CustomerDashboardPreference  # Add this import
)
from decimal import Decimal

def home(request):
    """Home page with featured products and categories"""
    categories = Category.objects.all()[:6]
    featured_products = Product.objects.filter(stock__gt=0).order_by('-created_at')[:8]
    
    context = {
        'categories': categories,
        'featured_products': featured_products,
    }
    return render(request, 'customer/home.html', context)

def product_list(request):
    """List all products with search and filter functionality"""
    products = Product.objects.filter(stock__gt=0)
    categories = Category.objects.all()
    
    # Handle search
    search_query = request.GET.get('search', '')
    if search_query:
        products = products.filter(name__icontains=search_query)
    
    # Handle category filter
    category_id = request.GET.get('category', '')
    if category_id and category_id.isdigit():
        products = products.filter(category_id=category_id)
    
    # Handle price sorting
    sort = request.GET.get('sort', '')
    if sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')
    elif sort == 'newest':
        products = products.order_by('-created_at')
    
    context = {
        'products': products,
        'categories': categories,
        'search_query': search_query,
        'selected_category': int(category_id) if category_id and category_id.isdigit() else None,
        'selected_sort': sort,
    }
    return render(request, 'customer/product_list.html', context)

def product_detail(request, pk):
    """Product detail page with add to cart functionality"""
    product = get_object_or_404(Product, pk=pk)
    related_products = Product.objects.filter(
        category=product.category, 
        stock__gt=0
    ).exclude(pk=pk).order_by('-created_at')[:4]
    
    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'customer/product_detail.html', context)

def product_by_category(request, category_id):
    """Show products filtered by category"""
    category = get_object_or_404(Category, pk=category_id)
    products = Product.objects.filter(category=category, stock__gt=0)
    categories = Category.objects.all()
    
    context = {
        'category': category,
        'products': products,
        'categories': categories,
        'selected_category': category_id,
    }
    return render(request, 'customer/product_list.html', context)

def _get_cart(request):
    """Helper function to get or create the cart in session"""
    if 'cart' not in request.session:
        request.session['cart'] = []
    return request.session['cart']

def _calculate_cart_totals(cart):
    """Helper function to calculate cart totals"""
    total_price = sum(Decimal(str(item['price'])) * item['quantity'] for item in cart)
    total_items = sum(item['quantity'] for item in cart)
    return total_price, total_items

def cart_view(request):
    """View the shopping cart"""
    cart = _get_cart(request)
    total_price, total_items = _calculate_cart_totals(cart)
    
    context = {
        'cart': cart,
        'total_price': total_price,
        'total_items': total_items,
    }
    return render(request, 'customer/cart.html', context)

def add_to_cart(request, product_id):
    """Add a product to the cart"""
    product = get_object_or_404(Product, pk=product_id)
    cart = _get_cart(request)
    
    quantity = int(request.POST.get('quantity', 1))
    
    # Check if the product is already in the cart
    for item in cart:
        if item['product_id'] == product_id:
            item['quantity'] += quantity
            request.session.modified = True
            messages.success(request, f'Added {quantity} more {product.name} to your cart!')
            return redirect('customer:cart')
    
    # If not, add it as a new item
    cart.append({
        'item_id': len(cart) + 1,
        'product_id': product_id,
        'name': product.name,
        'price': str(product.price),
        'quantity': quantity,
        'image_url': product.image.url if product.image else None,
    })
    
    request.session.modified = True
    messages.success(request, f'Added {product.name} to your cart!')
    return redirect('customer:cart')

def update_cart(request, item_id):
    """Update the quantity of an item in the cart"""
    cart = _get_cart(request)
    
    for item in cart:
        if item['item_id'] == item_id:
            new_quantity = int(request.POST.get('quantity', 1))
            item['quantity'] = new_quantity
            request.session.modified = True
            messages.success(request, 'Cart updated successfully!')
            break
    
    return redirect('customer:cart')

def remove_from_cart(request, item_id):
    """Remove an item from the cart"""
    cart = _get_cart(request)
    
    # Find and remove the item
    for i, item in enumerate(cart):
        if item['item_id'] == item_id:
            del cart[i]
            request.session.modified = True
            messages.success(request, 'Item removed from cart!')
            break
    
    # Recalculate item_id for remaining items
    for i, item in enumerate(cart):
        item['item_id'] = i + 1
    
    return redirect('customer:cart')

def checkout(request):
    """Checkout page with customer details form"""
    cart = _get_cart(request)
    if not cart:
        messages.warning(request, 'Your cart is empty!')
        return redirect('customer:cart')
    
    total_price, total_items = _calculate_cart_totals(cart)
    
    context = {
        'cart': cart,
        'total_price': total_price,
        'total_items': total_items,
    }
    return render(request, 'customer/checkout.html', context)

from django.shortcuts import redirect
from django.contrib import messages
from django.views.decorators.http import require_POST
from decimal import Decimal
from .models import Customer, Order, OrderItem, InventoryTransaction, Product

@require_POST
def confirm_order(request):
    """Process the order and save it to the database"""
    if request.method != 'POST':
        return redirect('customer:checkout')
    
    cart = _get_cart(request)
    if not cart:
        messages.warning(request, 'Your cart is empty!')
        return redirect('customer:cart')
    
    # Get customer information from form
    name = request.POST.get('name')
    email = request.POST.get('email')
    phone = request.POST.get('phone')
    address = request.POST.get('address')
    payment_method = request.POST.get('payment_method')
    
    # Check if the customer already exists
    try:
        # If the user is logged in, try to find the customer by user
        if request.user.is_authenticated:
            customer = Customer.objects.get(user=request.user)
            # Update customer details
            customer.name = name
            customer.phone = phone
            customer.address = address
            customer.save()
        else:
            # If the user is not logged in, try to find the customer by email
            customer = Customer.objects.get(email=email)
            # Update customer details
            customer.name = name
            customer.phone = phone
            customer.address = address
            customer.save()
    except Customer.DoesNotExist:
        # If the customer does not exist, create a new one
        defaults = {
            'name': name,
            'phone': phone,
            'address': address,
        }
        
        # If the user is logged in, associate the customer with the user
        if request.user.is_authenticated:
            defaults['user'] = request.user
        
        customer = Customer.objects.create(email=email, **defaults)
    
    # Calculate total
    total_price = sum(Decimal(item['price']) * item['quantity'] for item in cart)
    
    # Create order
    order = Order.objects.create(
        customer=customer,
        status='pending',
        shipping_address=address,
        payment_method=payment_method,
        total_amount=total_price,
    )
    
    # Create order items and update inventory
    for item in cart:
        product = Product.objects.get(pk=item['product_id'])
        
        # Create order item
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=item['quantity'],
            price=Decimal(item['price']),
        )
        
        # Update inventory
        product.stock -= item['quantity']
        product.save()
        
        # Create inventory transaction
        InventoryTransaction.objects.create(
            product=product,
            quantity=-item['quantity'],
            transaction_type='order',
            reference=f'Order #{order.id}',
        )
    
    # Clear the cart
    request.session['cart'] = []
    
    return redirect('customer:order_success', order_id=order.id)

def order_success(request, order_id):
    """Order success page"""
    order = get_object_or_404(Order, pk=order_id)
    
    context = {
        'order': order,
    }
    return render(request, 'customer/order_success.html', context)

def register(request):
    """User registration page"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Create a customer profile for the user if email is provided
            email = request.POST.get('email')
            if email:
                customer, created = Customer.objects.get_or_create(
                    email=email,
                    defaults={
                        'name': user.username,
                        'user': user
                    }
                )
                
                # If customer already exists with this email but no user, link them
                if not created and not customer.user:
                    customer.user = user
                    customer.save()
            
            login(request, user)
            messages.success(request, 'Registration successful. You are now logged in.')
            return redirect('customer:home')
    else:
        form = UserCreationForm()
    
    context = {
        'form': form,
    }
    return render(request, 'customer/register.html', context)

def login_view(request):
    """User login page"""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'Login successful.')
                # Redirect admin users to the admin dashboard
                if user.is_staff or user.is_superuser:
                    return redirect('/admin/')
                return redirect('customer:home')
    else:
        form = AuthenticationForm()
    
    context = {
        'form': form,
    }
    return render(request, 'customer/login.html', context)

def logout_view(request):
    """User logout"""
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('customer:home')

@login_required
def profile(request):
    """User profile page"""
    try:
        customer = Customer.objects.get(user=request.user)
        # Get or create dashboard preferences
        dashboard_pref, created = CustomerDashboardPreference.objects.get_or_create(customer=customer)
    except Customer.DoesNotExist:
        customer = None
        dashboard_pref = None
    
    # Handle profile update form
    if request.method == 'POST' and 'update_profile' in request.POST and customer:
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('customer:profile')
    
    context = {
        'customer': customer,
        'dashboard_pref': dashboard_pref,
    }
    return render(request, 'customer/profile.html', context)

@login_required
def order_history(request):
    """User order history page"""
    try:
        customer = Customer.objects.get(user=request.user)
        orders = Order.objects.filter(customer=customer).order_by('-order_date')
    except Customer.DoesNotExist:
        orders = []
    
    context = {
        'orders': orders,
    }
    return render(request, 'customer/order_history.html', context)

@login_required
def order_detail(request, order_id):
    """Order detail page"""
    try:
        customer = Customer.objects.get(user=request.user)
        order = get_object_or_404(Order, pk=order_id, customer=customer)
    except Customer.DoesNotExist:
        return redirect('customer:login')
    
    context = {
        'order': order,
    }
    return render(request, 'customer/order_detail.html', context)
    
@login_required
def order_tracking(request, order_id):
    """Order tracking page with real-time updates"""
    try:
        customer = Customer.objects.get(user=request.user)
        order = get_object_or_404(
            Order.objects.prefetch_related('items', 'status_history', 'delivery_locations'),
            pk=order_id, 
            customer=customer
        )
    except Customer.DoesNotExist:
        return redirect('customer:login')
    
    context = {
        'order': order,
    }
    return render(request, 'customer/order_tracking.html', context)

def scan_qr_code(request, order_id=None):
    """Process QR code scan for delivery tracking"""
    if request.GET.get('order_id'):
        order_id = request.GET.get('order_id')
        
    if order_id:
        # QR code has order ID
        order = get_object_or_404(Order, pk=order_id)
        
        # If the user is authenticated and is the order's customer or staff
        if (request.user.is_authenticated and 
            (request.user.is_staff or 
             (hasattr(request.user, 'customer') and order.customer == request.user.customer))):
            return redirect('customer:order_tracking', order_id=order.id)
        else:
            # For non-authenticated users or users who aren't the customer
            return render(request, 'customer/order_scan_result.html', {'order': order})
    
    # No order ID provided, show scan interface
    return render(request, 'customer/scan_qr.html')
    
@require_POST
@login_required
def update_order_status(request, order_id):
    """Update order status and location from QR scan (staff only)"""
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'error': 'Permission denied'})
        
    order = get_object_or_404(Order, pk=order_id)
    
    # Get data from POST
    status = request.POST.get('status')
    notes = request.POST.get('notes', '')
    latitude = request.POST.get('latitude')
    longitude = request.POST.get('longitude')
    location_name = request.POST.get('location_name', '')
    
    # Check if status is valid
    if status not in [s[0] for s in Order.STATUS_CHOICES]:
        return JsonResponse({'success': False, 'error': 'Invalid status'})
    
    # Update order status
    old_status = order.status
    order.status = status
    
    # If shipping status, add tracking info if provided
    if status == 'shipped' and not order.tracking_number:
        tracking_number = request.POST.get('tracking_number')
        delivery_partner = request.POST.get('delivery_partner')
        tracking_url = request.POST.get('tracking_url')
        
        if tracking_number:
            order.tracking_number = tracking_number
        if delivery_partner:
            order.delivery_partner = delivery_partner
        if tracking_url:
            order.tracking_url = tracking_url
    
    # If out for delivery or delivered, update estimated delivery
    if status in ['out_for_delivery', 'delivered'] and not order.estimated_delivery:
        order.estimated_delivery = timezone.now().date()
    
    # Save order changes
    order.save()
    
    # Create location update if coordinates provided
    if latitude and longitude:
        location = DeliveryLocation.objects.create(
            order=order,
            latitude=latitude,
            longitude=longitude,
            location_name=location_name,
            status_update=status,
            notes=notes
        )
    
    # StatusHistory is created by the signal handler
    
    return JsonResponse({
        'success': True,
        'order_id': order.id,
        'status': order.get_status_display(),
        'message': f'Order status updated from {old_status} to {status}'
    })