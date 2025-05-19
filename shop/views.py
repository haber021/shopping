from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Sum, Count, Q, F  # Add F here
from django.utils import timezone
from datetime import datetime, timedelta
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from django.db import transaction, models  # Add models here

from .models import (
    Product, Order, OrderItem, Customer, 
    InventoryTransaction, Supplier, Category, Setting
)
from .forms import (
    ProductForm, OrderForm, CustomerForm, RestockForm, 
    OrderUpdateForm, OrderItemForm, SupplierForm, CategoryForm,
    DateRangeForm, GeneralSettingsForm, PaymentSettingsForm,
    ShippingSettingsForm, UserForm
)
from .utils import get_setting, set_setting






@login_required
def dashboard(request):
    # Redirect non-admin users to the home page
    if not request.user.is_staff and not request.user.is_superuser:
        return redirect('customer:home')  # Ensure you return the redirect response
    
    # Get quick stats data
    total_orders = Order.objects.count()
    total_revenue = Order.objects.aggregate(total=Sum('total_amount'))['total'] or 0
    low_stock_count = Product.objects.filter(stock__lte=F('reorder_level')).count()
    pending_orders = Order.objects.filter(status='pending').count()
    
    # Get recent activities (last 10 orders)
    recent_orders = Order.objects.order_by('-order_date')[:10]
    
    # Get top selling products
    top_products = OrderItem.objects.values('product__name').annotate(
        total_quantity=Sum('quantity')
    ).order_by('-total_quantity')[:5]
    
    context = {
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'low_stock_count': low_stock_count,
        'pending_orders': pending_orders,
        'recent_orders': recent_orders,
        'top_products': top_products,
    }
    return render(request, 'dashboard.html', context)

# Product views
@login_required
def product_list(request):
    products = Product.objects.all()
    
    # Filter by category if provided
    category_id = request.GET.get('category')
    if category_id:
        products = products.filter(category_id=category_id)
    
    # Filter by stock status if provided
    stock_status = request.GET.get('stock_status')
    if stock_status == 'low':
        products = products.filter(stock__lte=models.F('reorder_level'))
    elif stock_status == 'out':
        products = products.filter(stock=0)
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(products, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    categories = Category.objects.all()
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'search_query': search_query,
    }
    return render(request, 'products/list.html', context)

@login_required
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, f'Product "{product.name}" created successfully.')
            return redirect('shop:product_list')
    else:
        form = ProductForm()
    
    context = {
        'form': form,
        'title': 'Create Product',
    }
    return render(request, 'products/detail.html', context)

@login_required
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    context = {
        'product': product,
    }
    return render(request, 'products/detail.html', context)

@login_required
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, f'Product "{product.name}" updated successfully.')
            return redirect('shop:product_list')
    else:
        form = ProductForm(instance=product)
    
    context = {
        'form': form,
        'product': product,
        'title': 'Edit Product',
    }
    return render(request, 'products/detail.html', context)

@login_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        name = product.name
        product.delete()
        messages.success(request, f'Product "{name}" deleted successfully.')
        return redirect('shop:product_list')
    
    context = {
        'product': product,
    }
    return render(request, 'products/delete.html', context)

# Order views
@login_required
def order_list(request):
    orders = Order.objects.all().order_by('-order_date')
    
    # Filter by status if provided
    status = request.GET.get('status')
    if status:
        orders = orders.filter(status=status)
    
    # Filter by date range if provided
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    if start_date and end_date:
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            end_date = datetime.combine(end_date, datetime.max.time())
            orders = orders.filter(order_date__range=[start_date, end_date])
        except ValueError:
            messages.error(request, 'Invalid date format')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        orders = orders.filter(
            Q(id__icontains=search_query) | 
            Q(customer__name__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(orders, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_choices': Order.STATUS_CHOICES,
    }
    return render(request, 'orders/list.html', context)

@login_required
def order_create(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            # Calculate total amount based on order items
            total_amount = 0
            
            # Create the order first
            order.total_amount = total_amount
            order.save()
            
            # Process order items
            for i in range(int(request.POST.get('item_count', 0))):
                product_id = request.POST.get(f'item_product_{i}')
                quantity = request.POST.get(f'item_quantity_{i}')
                
                if product_id and quantity:
                    product = get_object_or_404(Product, id=product_id)
                    
                    # Update product stock
                    with transaction.atomic():
                        if product.stock >= int(quantity):
                            product.stock -= int(quantity)
                            product.save()
                            
                            # Create order item
                            OrderItem.objects.create(
                                order=order,
                                product=product,
                                quantity=int(quantity),
                                price=product.price
                            )
                            
                            # Create inventory transaction
                            InventoryTransaction.objects.create(
                                product=product,
                                quantity=-int(quantity),
                                transaction_type='order',
                                reference=f'Order #{order.id}'
                            )
                            
                            # Update total amount
                            total_amount += product.price * int(quantity)
                        else:
                            messages.error(request, f'Not enough stock for {product.name}.')
                            order.delete()
                            return redirect('shop:order_create')
            
            # Update the order total
            order.total_amount = total_amount
            order.save()
            
            messages.success(request, f'Order #{order.id} created successfully.')
            return redirect('shop:order_list')
    else:
        form = OrderForm()
    
    # Get products for the item form
    products = Product.objects.filter(stock__gt=0)
    
    context = {
        'form': form,
        'products': products,
        'title': 'Create Order',
    }
    return render(request, 'orders/detail.html', context)

@login_required
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    order_items = order.items.all()
    
    context = {
        'order': order,
        'order_items': order_items,
    }
    return render(request, 'orders/detail.html', context)

@login_required
def order_update(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        form = OrderUpdateForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            messages.success(request, f'Order #{order.id} updated successfully.')
            return redirect('shop:order_list')
    else:
        form = OrderUpdateForm(instance=order)
    
    context = {
        'form': form,
        'order': order,
        'order_items': order.items.all(),
        'title': 'Update Order Status',
    }
    return render(request, 'orders/detail.html', context)

@login_required
def order_cancel(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        # Check if order can be cancelled (not shipped or delivered)
        if order.status in ['shipped', 'delivered']:
            messages.error(request, f'Cannot cancel order #{order.id} as it is already {order.status}.')
            return redirect('shop:order_detail', pk=order.pk)
        
        # Return items to inventory
        with transaction.atomic():
            for item in order.items.all():
                # Update product stock
                item.product.stock += item.quantity
                item.product.save()
                
                # Create inventory transaction
                InventoryTransaction.objects.create(
                    product=item.product,
                    quantity=item.quantity,
                    transaction_type='adjustment',
                    reference=f'Cancelled Order #{order.id}'
                )
            
            # Update order status
            order.status = 'cancelled'
            order.save()
        
        messages.success(request, f'Order #{order.id} cancelled successfully.')
        return redirect('shop:order_list')
    
    context = {
        'order': order,
    }
    return render(request, 'orders/cancel.html', context)

# Inventory views
@login_required
def inventory_list(request):
    products = Product.objects.all()
    
    # Filter by low stock
    filter_option = request.GET.get('filter')
    if filter_option == 'low_stock':
        products = products.filter(stock__lte=models.F('reorder_level'))
    elif filter_option == 'out_of_stock':
        products = products.filter(stock=0)
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(products, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'filter_option': filter_option,
    }
    return render(request, 'inventory/list.html', context)

@login_required
def inventory_restock(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        form = RestockForm(request.POST, product_id=product_id)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.transaction_type = 'restock'
            transaction.save()
            
            # Update product stock
            product.stock += transaction.quantity
            product.save()
            
            messages.success(request, f'Successfully restocked {transaction.quantity} units of {product.name}.')
            return redirect('shop:inventory_list')
    else:
        form = RestockForm(product_id=product_id)
    
    context = {
        'form': form,
        'product': product,
    }
    return render(request, 'inventory/restock.html', context)

# Customer views
@login_required
def customer_list(request):
    customers = Customer.objects.all()
    
    # Filter by activity status
    status = request.GET.get('status')
    if status == 'active':
        # Customers with at least one order
        customers = customers.filter(orders__isnull=False).distinct()
    elif status == 'inactive':
        # Customers with no orders
        customers = customers.filter(orders__isnull=True)
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        customers = customers.filter(
            Q(name__icontains=search_query) | 
            Q(email__icontains=search_query) |
            Q(phone__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(customers, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
    }
    return render(request, 'customers/list.html', context)

@login_required
def customer_create(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save()
            messages.success(request, f'Customer "{customer.name}" created successfully.')
            return redirect('shop:customer_list')
    else:
        form = CustomerForm()
    
    context = {
        'form': form,
        'title': 'Create Customer',
    }
    return render(request, 'customers/detail.html', context)

@login_required
def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    orders = customer.orders.all().order_by('-order_date')
    
    context = {
        'customer': customer,
        'orders': orders,
    }
    return render(request, 'customers/detail.html', context)

@login_required
def customer_edit(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, f'Customer "{customer.name}" updated successfully.')
            return redirect('shop:customer_list')
    else:
        form = CustomerForm(instance=customer)
    
    context = {
        'form': form,
        'customer': customer,
        'title': 'Edit Customer',
    }
    return render(request, 'customers/detail.html', context)

# Supplier views
@login_required
def supplier_list(request):
    suppliers = Supplier.objects.all()
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        suppliers = suppliers.filter(
            Q(name__icontains=search_query) | 
            Q(contact_person__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(suppliers, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
    }
    return render(request, 'suppliers/list.html', context)

@login_required
def supplier_create(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            supplier = form.save()
            messages.success(request, f'Supplier "{supplier.name}" created successfully.')
            return redirect('shop:supplier_list')
    else:
        form = SupplierForm()
    
    context = {
        'form': form,
        'title': 'Create Supplier',
    }
    return render(request, 'suppliers/detail.html', context)

@login_required
def supplier_detail(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    products = supplier.products.all()
    
    context = {
        'supplier': supplier,
        'products': products,
    }
    return render(request, 'suppliers/detail.html', context)

@login_required
def supplier_edit(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            messages.success(request, f'Supplier "{supplier.name}" updated successfully.')
            return redirect('shop:supplier_list')
    else:
        form = SupplierForm(instance=supplier)
    
    context = {
        'form': form,
        'supplier': supplier,
        'title': 'Edit Supplier',
    }
    return render(request, 'suppliers/detail.html', context)

# Reports views
@login_required
def report_index(request):
    context = {}
    return render(request, 'reports/index.html', context)

@login_required
def sales_report(request):
    if request.method == 'POST':
        form = DateRangeForm(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            
            # Get orders within the date range
            orders = Order.objects.filter(
                order_date__date__gte=start_date,
                order_date__date__lte=end_date
            )
            
            total_sales = orders.aggregate(total=Sum('total_amount'))['total'] or 0
            order_count = orders.count()
            
            # Sales by day
            sales_by_day = orders.values('order_date__date').annotate(
                total=Sum('total_amount')
            ).order_by('order_date__date')
            
            # Sales by product category
            sales_by_category = OrderItem.objects.filter(
                order__in=orders
            ).values('product__category__name').annotate(
                total=Sum('price')
            ).order_by('-total')
            
            context = {
                'form': form,
                'total_sales': total_sales,
                'order_count': order_count,
                'sales_by_day': list(sales_by_day),
                'sales_by_category': list(sales_by_category),
                'start_date': start_date,
                'end_date': end_date,
                'report_generated': True,
            }
        else:
            context = {'form': form}
    else:
        # Default to last 30 days
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)
        form = DateRangeForm(initial={'start_date': start_date, 'end_date': end_date})
        context = {'form': form}
        
    return render(request, 'reports/sales.html', context)

@login_required
def inventory_report(request):
    # Get all products with stock information
    products = Product.objects.all()
    
    # Count products by category
    products_by_category = products.values('category__name').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Count low stock products by category
    low_stock_by_category = products.filter(
        stock__lte=models.F('reorder_level')
    ).values('category__name').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Calculate total inventory value
    total_inventory_value = sum(product.stock * product.price for product in products)
    
    # Get top products that need restocking
    needs_restocking = products.filter(
        stock__lte=models.F('reorder_level')
    ).order_by('stock')[:10]
    
    context = {
        'products_by_category': list(products_by_category),
        'low_stock_by_category': list(low_stock_by_category),
        'total_inventory_value': total_inventory_value,
        'needs_restocking': needs_restocking,
    }
    return render(request, 'reports/inventory.html', context)

@login_required
def customers_report(request):
    # Get all customers
    customers = Customer.objects.all()
    
    # Count customers with orders
    active_customers = customers.filter(orders__isnull=False).distinct().count()
    
    # Count customers without orders
    inactive_customers = customers.filter(orders__isnull=True).count()
    
    # Get top customers by total order value
    top_customers = Customer.objects.annotate(
        total_spent=Sum('orders__total_amount')
    ).filter(total_spent__isnull=False).order_by('-total_spent')[:10]
    
    # Get top customers by order count
    most_frequent = Customer.objects.annotate(
        order_count=Count('orders')
    ).filter(order_count__gt=0).order_by('-order_count')[:10]
    
    context = {
        'total_customers': customers.count(),
        'active_customers': active_customers,
        'inactive_customers': inactive_customers,
        'top_customers': top_customers,
        'most_frequent': most_frequent,
    }
    return render(request, 'reports/customers.html', context)

# Settings views
@login_required
def settings_general(request):
    if request.method == 'POST':
        form = GeneralSettingsForm(request.POST)
        if form.is_valid():
            for key, value in form.cleaned_data.items():
                set_setting(key, value)
            messages.success(request, 'General settings updated successfully.')
            return redirect('shop:settings_general')
    else:
        initial_data = {
            'company_name': get_setting('company_name', 'My Company'),
            'company_address': get_setting('company_address', ''),
            'company_email': get_setting('company_email', ''),
            'company_phone': get_setting('company_phone', ''),
        }
        form = GeneralSettingsForm(initial=initial_data)
    
    context = {
        'form': form,
        'active_tab': 'general',
    }
    return render(request, 'settings/general.html', context)

@login_required
def settings_payment(request):
    if request.method == 'POST':
        form = PaymentSettingsForm(request.POST)
        if form.is_valid():
            for key, value in form.cleaned_data.items():
                set_setting(key, value)
            messages.success(request, 'Payment settings updated successfully.')
            return redirect('shop:settings_payment')
    else:
        initial_data = {
            'tax_rate': get_setting('tax_rate', '0.00'),
            'payment_methods': get_setting('payment_methods', 'Cash\nCredit Card\nBank Transfer'),
        }
        form = PaymentSettingsForm(initial=initial_data)
    
    context = {
        'form': form,
        'active_tab': 'payment',
    }
    return render(request, 'settings/payment.html', context)

@login_required
def settings_shipping(request):
    if request.method == 'POST':
        form = ShippingSettingsForm(request.POST)
        if form.is_valid():
            for key, value in form.cleaned_data.items():
                set_setting(key, value)
            messages.success(request, 'Shipping settings updated successfully.')
            return redirect('shop:settings_shipping')
    else:
        initial_data = {
            'shipping_methods': get_setting('shipping_methods', 'Standard Shipping\nExpress Shipping'),
            'default_shipping_fee': get_setting('default_shipping_fee', '10.00'),
        }
        form = ShippingSettingsForm(initial=initial_data)
    
    context = {
        'form': form,
        'active_tab': 'shipping',
    }
    return render(request, 'settings/shipping.html', context)

@login_required
def settings_users(request):
    users = User.objects.all()
    
    context = {
        'users': users,
        'active_tab': 'users',
    }
    return render(request, 'settings/users.html', context)

@login_required
def user_create(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, f'User "{user.username}" created successfully.')
            return redirect('shop:settings_users')
    else:
        form = UserForm()
    
    context = {
        'form': form,
        'title': 'Create User',
    }
    return render(request, 'settings/user_form.html', context)

@login_required
def user_edit(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            user = form.save(commit=False)
            if form.cleaned_data['password']:
                user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, f'User "{user.username}" updated successfully.')
            return redirect('shop:settings_users')
    else:
        # Don't include password in the form
        form = UserForm(instance=user)
    
    context = {
        'form': form,
        'user_obj': user,
        'title': 'Edit User',
    }
    return render(request, 'settings/user_form.html', context)


@login_required
def api_dashboard_stats(request):
    # Check if the user is a staff member or superuser
    if not request.user.is_staff and not request.user.is_superuser:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    # Get quick stats data
    total_orders = Order.objects.count()
    total_revenue = Order.objects.aggregate(total=Sum('total_amount'))['total'] or 0
    low_stock_count = Product.objects.filter(stock__lte=F('reorder_level')).count()
    pending_orders = Order.objects.filter(status='pending').count()
    
    data = {
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'low_stock_count': low_stock_count,
        'pending_orders': pending_orders,
    }
    return JsonResponse(data)

@login_required
def api_sales_chart(request):
    # Get sales data for the last 30 days
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=30)
    
    # Daily sales
    daily_sales = Order.objects.filter(
        order_date__date__gte=start_date,
        order_date__date__lte=end_date
    ).values('order_date__date').annotate(
        total=Sum('total_amount')
    ).order_by('order_date__date')
    
    # Convert to format suitable for Chart.js
    labels = []
    data = []
    
    current_date = start_date
    while current_date <= end_date:
        labels.append(current_date.strftime('%Y-%m-%d'))
        
        # Find sales for this date
        sale = next((item for item in daily_sales if item['order_date__date'] == current_date), None)
        data.append(float(sale['total']) if sale else 0)
        
        current_date += timedelta(days=1)
    
    chart_data = {
        'labels': labels,
        'datasets': [{
            'label': 'Daily Sales',
            'data': data,
            'borderColor': 'rgb(75, 192, 192)',
            'tension': 0.1
        }]
    }
    
    return JsonResponse(chart_data)

@login_required
def api_inventory_chart(request):
    # Get inventory data by category
    inventory_by_category = Product.objects.values('category__name').annotate(
        total_stock=Sum('stock')
    ).order_by('-total_stock')
    
    # Convert to format suitable for Chart.js
    labels = [item['category__name'] for item in inventory_by_category]
    data = [item['total_stock'] for item in inventory_by_category]
    
    chart_data = {
        'labels': labels,
        'datasets': [{
            'label': 'Stock by Category',
            'data': data,
            'backgroundColor': [
                'rgba(255, 99, 132, 0.2)',
                'rgba(54, 162, 235, 0.2)',
                'rgba(255, 206, 86, 0.2)',
                'rgba(75, 192, 192, 0.2)',
                'rgba(153, 102, 255, 0.2)',
            ],
            'borderColor': [
                'rgba(255, 99, 132, 1)',
                'rgba(54, 162, 235, 1)',
                'rgba(255, 206, 86, 1)',
                'rgba(75, 192, 192, 1)',
                'rgba(153, 102, 255, 1)',
            ],
            'borderWidth': 1
        }]
    }
    
    return JsonResponse(chart_data)


from rest_framework.decorators import api_view
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from .models import Order, Product
from django.db.models import Sum

@api_view(['GET'])
def api_sales_chart(request):
    # Get sales data for the last 30 days
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=30)
    
    # Daily sales
    daily_sales = Order.objects.filter(
        order_date__date__gte=start_date,
        order_date__date__lte=end_date
    ).values('order_date__date').annotate(
        total=Sum('total_amount')
    ).order_by('order_date__date')
    
    # Convert to format suitable for Chart.js
    labels = []
    data = []
    
    current_date = start_date
    while current_date <= end_date:
        labels.append(current_date.strftime('%Y-%m-%d'))
        
        # Find sales for this date
        sale = next((item for item in daily_sales if item['order_date__date'] == current_date), None)
        data.append(float(sale['total']) if sale else 0)
        
        current_date += timedelta(days=1)
    
    chart_data = {
        'labels': labels,
        'datasets': [{
            'label': 'Daily Sales',
            'data': data,
            'borderColor': 'rgb(75, 192, 192)',
            'tension': 0.1
        }]
    }
    
    return JsonResponse(chart_data)

@api_view(['GET'])
def api_inventory_chart(request):
    # Get inventory data by category
    inventory_by_category = Product.objects.values('category__name').annotate(
        total_stock=Sum('stock')
    ).order_by('-total_stock')
    
    # Convert to format suitable for Chart.js
    labels = [item['category__name'] for item in inventory_by_category]
    data = [item['total_stock'] for item in inventory_by_category]
    
    chart_data = {
        'labels': labels,
        'datasets': [{
            'label': 'Stock by Category',
            'data': data,
            'backgroundColor': [
                'rgba(255, 99, 132, 0.2)',
                'rgba(54, 162, 235, 0.2)',
                'rgba(255, 206, 86, 0.2)',
                'rgba(75, 192, 192, 0.2)',
                'rgba(153, 102, 255, 0.2)',
            ],
            'borderColor': [
                'rgba(255, 99, 132, 1)',
                'rgba(54, 162, 235, 1)',
                'rgba(255, 206, 86, 1)',
                'rgba(75, 192, 192, 1)',
                'rgba(153, 102, 255, 1)',
            ],
            'borderWidth': 1
        }]
    }
    
    return JsonResponse(chart_data)