from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.http import JsonResponse, HttpResponse
from django.db.models import Sum, Count, F, Q, Avg
from django.utils import timezone
from datetime import timedelta
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.template.loader import render_to_string

from .models import (
    Product, Category, Customer, Order, OrderItem, 
    Supplier, Inventory, InventoryTransaction, CompanySettings
)
from .forms import (
    ProductForm, CategoryForm, CustomerForm, OrderForm, OrderItemFormSet,
    SupplierForm, InventoryForm, RestockForm, CompanySettingsForm
)

# Authentication Views
class CustomLoginView(LoginView):
    template_name = 'auth/login.html'
    redirect_authenticated_user = True

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'auth/register.html', {'form': form})

# Dashboard View
@login_required
def dashboard(request):
    # Recent orders
    recent_orders = Order.objects.all().order_by('-created_at')[:5]
    
    # Quick stats
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status='PENDING').count()
    
    # Revenue calculation (total of all orders)
    revenue = OrderItem.objects.aggregate(
        total=Sum(F('price') * F('quantity'))
    )['total'] or 0
    
    # Low stock alerts
    low_stock_items = Inventory.objects.filter(
        current_stock__lte=F('reorder_level')
    ).count()
    
    # Get data for charts
    # Sales trend for the last 30 days
    thirty_days_ago = timezone.now() - timedelta(days=30)
    orders_by_day = Order.objects.filter(
        created_at__gte=thirty_days_ago
    ).values('created_at__date').annotate(
        count=Count('id'),
        revenue=Sum(F('items__price') * F('items__quantity'))
    ).order_by('created_at__date')
    
    # Inventory levels
    inventory_data = Inventory.objects.select_related('product').all()[:10]
    
    context = {
        'recent_orders': recent_orders,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'revenue': revenue,
        'low_stock_items': low_stock_items,
        'orders_by_day': list(orders_by_day),
        'inventory_data': inventory_data,
    }
    return render(request, 'dashboard.html', context)

# Product Views
class ProductListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search', '')
        category = self.request.GET.get('category', '')
        
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) | 
                Q(description__icontains=search_query)
            )
        
        if category:
            queryset = queryset.filter(category_id=category)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context

class ProductDetailView(LoginRequiredMixin, DetailView):
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'

class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'products/product_form.html'
    success_url = reverse_lazy('product-list')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Create inventory record for new product
        Inventory.objects.create(
            product=self.object,
            current_stock=0,
            reorder_level=10
        )
        
        messages.success(self.request, 'Product created successfully!')
        return response

class ProductUpdateView(LoginRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'products/product_form.html'
    success_url = reverse_lazy('product-list')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Product updated successfully!')
        return response

class ProductDeleteView(LoginRequiredMixin, DeleteView):
    model = Product
    template_name = 'products/product_confirm_delete.html'
    success_url = reverse_lazy('product-list')
    
    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        messages.success(request, 'Product deleted successfully!')
        return response

# Order Views
class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'orders/order_list.html'
    context_object_name = 'orders'
    
    def get_queryset(self):
        queryset = super().get_queryset().select_related('customer')
        status = self.request.GET.get('status', '')
        search_query = self.request.GET.get('search', '')
        
        if status:
            queryset = queryset.filter(status=status)
        
        if search_query:
            queryset = queryset.filter(
                Q(customer__name__icontains=search_query) | 
                Q(id__icontains=search_query)
            )
            
        return queryset

class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'orders/order_detail.html'
    context_object_name = 'order'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['items'] = self.object.items.select_related('product').all()
        return context

@login_required
def update_order_status(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Order.STATUS_CHOICES).keys():
            order.status = new_status
            order.save()
            messages.success(request, f'Order #{order.id} status updated to {order.get_status_display()}')
        else:
            messages.error(request, 'Invalid status')
    return redirect('order-detail', pk=pk)

# Inventory Views
class InventoryListView(LoginRequiredMixin, ListView):
    model = Inventory
    template_name = 'inventory/inventory_list.html'
    context_object_name = 'inventory_items'
    
    def get_queryset(self):
        queryset = super().get_queryset().select_related('product')
        filter_option = self.request.GET.get('filter', '')
        search_query = self.request.GET.get('search', '')
        
        if filter_option == 'low_stock':
            queryset = queryset.filter(current_stock__lte=F('reorder_level'))
        elif filter_option == 'out_of_stock':
            queryset = queryset.filter(current_stock=0)
        
        if search_query:
            queryset = queryset.filter(product__name__icontains=search_query)
            
        return queryset

@login_required
def restock_inventory(request, pk):
    inventory = get_object_or_404(Inventory, pk=pk)
    
    if request.method == 'POST':
        form = RestockForm(request.POST)
        if form.is_valid():
            quantity = form.cleaned_data['quantity']
            notes = form.cleaned_data['notes']
            
            # Update inventory
            inventory.current_stock += quantity
            inventory.save()
            
            # Create transaction record
            InventoryTransaction.objects.create(
                inventory=inventory,
                quantity=quantity,
                transaction_type='IN',
                notes=notes
            )
            
            messages.success(request, f'{quantity} units added to {inventory.product.name}')
            return redirect('inventory-list')
    else:
        form = RestockForm()
    
    return render(request, 'inventory/restock_form.html', {
        'form': form,
        'inventory': inventory
    })

# Customer Views
class CustomerListView(LoginRequiredMixin, ListView):
    model = Customer
    template_name = 'customers/customer_list.html'
    context_object_name = 'customers'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search', '')
        
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) | 
                Q(email__icontains=search_query) |
                Q(phone__icontains=search_query)
            )
            
        return queryset

class CustomerDetailView(LoginRequiredMixin, DetailView):
    model = Customer
    template_name = 'customers/customer_detail.html'
    context_object_name = 'customer'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['orders'] = self.object.orders.all().order_by('-created_at')
        return context

class CustomerCreateView(LoginRequiredMixin, CreateView):
    model = Customer
    form_class = CustomerForm
    template_name = 'customers/customer_form.html'
    success_url = reverse_lazy('customer-list')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Customer created successfully!')
        return response

class CustomerUpdateView(LoginRequiredMixin, UpdateView):
    model = Customer
    form_class = CustomerForm
    template_name = 'customers/customer_form.html'
    success_url = reverse_lazy('customer-list')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Customer updated successfully!')
        return response

# Reports Views
@login_required
def reports_view(request):
    report_type = request.GET.get('report_type', 'sales')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    # Default to last 30 days if no dates provided
    if not date_from or not date_to:
        date_to = timezone.now().date()
        date_from = date_to - timedelta(days=30)
    
    if report_type == 'sales':
        # Sales report data
        orders = Order.objects.filter(
            created_at__date__range=[date_from, date_to]
        )
        
        # Daily sales data
        sales_by_day = orders.values('created_at__date').annotate(
            count=Count('id'),
            revenue=Sum(F('items__price') * F('items__quantity'))
        ).order_by('created_at__date')
        
        # Top selling products
        top_products = OrderItem.objects.filter(
            order__created_at__date__range=[date_from, date_to]
        ).values('product__name').annotate(
            total_sold=Sum('quantity'),
            revenue=Sum(F('price') * F('quantity'))
        ).order_by('-total_sold')[:10]
        
        context = {
            'report_type': report_type,
            'date_from': date_from,
            'date_to': date_to,
            'sales_by_day': list(sales_by_day),
            'top_products': top_products,
            'total_orders': orders.count(),
            'total_revenue': orders.aggregate(
                total=Sum(F('items__price') * F('items__quantity'))
            )['total'] or 0,
        }
        
    @login_required
def process_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'process':
            order.mark_as_processing()
            send_order_status_update(order)
            
        elif action == 'ship':
            tracking_number = request.POST.get('tracking_number')
            delivery_partner = request.POST.get('delivery_partner')
            order.mark_as_shipped(tracking_number, delivery_partner)
            send_order_status_update(order)
            
        elif action == 'deliver':
            order.mark_as_delivered()
            send_order_status_update(order)
            
        elif action == 'complete':
            order.mark_as_completed()
            send_order_status_update(order)
            
        elif action == 'cancel':
            order.mark_as_cancelled()
            send_order_status_update(order)
    
    return redirect('order_detail', order_id=order.id)

elif report_type == 'inventory':
        # Inventory report data
        inventory_data = Inventory.objects.all().select_related('product')
        
        # Calculate inventory value
        inventory_value = sum(item.current_stock * item.product.price for item in inventory_data)
        
        # Low stock items
        low_stock_items = inventory_data.filter(current_stock__lte=F('reorder_level'))
        
        context = {
            'report_type': report_type,
            'date_from': date_from,
            'date_to': date_to,
            'inventory_data': inventory_data,
            'inventory_value': inventory_value,
            'low_stock_count': low_stock_items.count(),
            'out_of_stock_count': inventory_data.filter(current_stock=0).count(),
        }
        
    elif report_type == 'customer':
        # Customer report data
        top_customers = Customer.objects.annotate(
            order_count=Count('orders'),
            total_spent=Sum(F('orders__items__price') * F('orders__items__quantity'))
        ).order_by('-total_spent')[:10]
        
        # New customers in date range
        new_customers = Customer.objects.filter(
            created_at__date__range=[date_from, date_to]
        ).count()
        
        context = {
            'report_type': report_type,
            'date_from': date_from,
            'date_to': date_to,
            'top_customers': top_customers,
            'new_customers': new_customers,
            'total_customers': Customer.objects.count(),
        }
    
    else:
        context = {
            'report_type': 'unknown',
        }
    
    return render(request, 'reports/report_list.html', context)

# Settings Views
@login_required
def settings_view(request):
    # Try to get existing settings or create default
    try:
        settings = CompanySettings.objects.first()
        if not settings:
            settings = CompanySettings.objects.create(
                company_name="My Company",
                address="123 Main St",
                email="contact@example.com",
                phone="123-456-7890"
            )
    except Exception:
        settings = CompanySettings(
            company_name="My Company",
            address="123 Main St",
            email="contact@example.com",
            phone="123-456-7890"
        )
    
    if request.method == 'POST':
        form = CompanySettingsForm(request.POST, instance=settings)
        if form.is_valid():
            form.save()
            messages.success(request, 'Settings updated successfully!')
            return redirect('settings')
    else:
        form = CompanySettingsForm(instance=settings)
    
    return render(request, 'settings/settings.html', {'form': form})

# HTMX Views for dynamic content
@login_required
@require_http_methods(["GET"])
def htmx_product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    html = render_to_string('products/product_detail_partial.html', {'product': product}, request=request)
    return HttpResponse(html)

@login_required
@require_http_methods(["GET"])
def htmx_order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    html = render_to_string('orders/order_detail_partial.html', {'order': order}, request=request)
    return HttpResponse(html)

@login_required
@require_http_methods(["GET"])
def htmx_customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    html = render_to_string('customers/customer_detail_partial.html', {'customer': customer}, request=request)
    return HttpResponse(html)

# API for Charts
@login_required
def sales_chart_data(request):
    days = int(request.GET.get('days', 30))
    start_date = timezone.now() - timedelta(days=days)
    
    orders_by_day = Order.objects.filter(
        created_at__gte=start_date
    ).values('created_at__date').annotate(
        total=Sum(F('items__price') * F('items__quantity')),
        count=Count('id')
    ).order_by('created_at__date')
    
    data = {
        'labels': [str(entry['created_at__date']) for entry in orders_by_day],
        'revenue': [float(entry['total'] or 0) for entry in orders_by_day],
        'count': [entry['count'] for entry in orders_by_day],
    }
    
    return JsonResponse(data)

@login_required
def inventory_chart_data(request):
    inventory_data = Inventory.objects.select_related('product').all()[:15]
    
    data = {
        'labels': [item.product.name for item in inventory_data],
        'current_stock': [item.current_stock for item in inventory_data],
        'reorder_level': [item.reorder_level for item in inventory_data],
    }
    
    return JsonResponse(data)
