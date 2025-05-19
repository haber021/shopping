from django.shortcuts import render, redirect
from PS.models import ActivityLog, Notification
from django.contrib.auth.decorators import login_required
from .models import (
    Supplier,
    Product,
    Inventory,
    Order,
    OrderItem,
)

def home(request):
    """Home page view - redirects to dashboard if logged in."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'core/home.html')

@login_required
def dashboard(request):
    """Dashboard view shows key metrics and recent activities."""
    # Get counts for dashboard stats
    total_products = Product.objects.count()
    active_suppliers = Supplier.objects.filter(status='active').count()
    pending_orders = Order.objects.filter(status='pending').count()
    
    # Get low stock items
    low_stock_items = []
    inventory_items = Inventory.objects.select_related('product__supplier').all()
    for inv in inventory_items:
        if inv.current_stock < inv.product.minimum_stock:
            low_stock_items.append({
                'id': inv.product.id,
                'name': inv.product.name,
                'sku': inv.product.sku,
                'current_stock': inv.current_stock,
                'minimum_stock': inv.product.minimum_stock,
                'supplier': {
                    'id': inv.product.supplier.id,
                    'name': inv.product.supplier.name
                },
                'status': inv.status
            })
    
    # Get recent activity logs
    recent_activities = ActivityLog.objects.all().order_by('-timestamp')[:10]
    
    # Get unread notifications
    notifications = Notification.objects.filter(read=False)
    
    context = {
        'total_products': total_products,
        'active_suppliers': active_suppliers,
        'pending_orders': pending_orders,
        'low_stock_items': low_stock_items,
        'low_stock_count': len(low_stock_items),
        'recent_activities': recent_activities,
        'notifications': notifications,
    }
    
    return render(request, 'core/dashboard.html', context)

@login_required
def suppliers(request):
    """View for managing suppliers."""
    suppliers_list = Supplier.objects.all()
    context = {
        'suppliers': suppliers_list
    }
    return render(request, 'core/suppliers.html', context)

@login_required
def products(request):
    """View for managing products."""
    products_list = Product.objects.select_related('supplier').all()
    suppliers_list = Supplier.objects.filter(status='active')
    context = {
        'products': products_list,
        'suppliers': suppliers_list
    }
    return render(request, 'core/products.html', context)

@login_required
def inventory(request):
    """View for managing inventory."""
    inventory_list = Inventory.objects.select_related('product').all()
    context = {
        'inventory': inventory_list
    }
    return render(request, 'core/inventory.html', context)

@login_required
def orders(request):
    """View for managing orders."""
    orders_list = Order.objects.select_related('supplier').all()
    suppliers_list = Supplier.objects.filter(status='active')
    products_list = Product.objects.select_related('supplier').all()
    context = {
        'orders': orders_list,
        'suppliers': suppliers_list,
        'products': products_list
    }
    return render(request, 'core/orders.html', context)
