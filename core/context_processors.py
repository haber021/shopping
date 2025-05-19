from django.db.models import Q, Count, F
from django.utils import timezone
from datetime import timedelta

def navbar_context(request):
    """
    Context processor to add common data to all templates.
    """
    # Only process if user is authenticated
    if not request.user.is_authenticated:
        return {}
    
    # Import models only when needed to avoid circular imports
    from .models import Order, Inventory, Product
    
    # Get notifications
    notifications = []
    
    # Low stock alerts
    low_stock_items = Inventory.objects.filter(
        current_stock__lte=F('reorder_level')
    ).count()
    
    if low_stock_items > 0:
        notifications.append({
            'title': f'{low_stock_items} items low on stock',
            'url': '/inventory/?filter=low_stock',
            'time': timezone.now()
        })
    
    # Recent pending orders
    recent_pending_orders = Order.objects.filter(
        status='PENDING',
        created_at__gte=timezone.now() - timedelta(days=1)
    ).count()
    
    if recent_pending_orders > 0:
        notifications.append({
            'title': f'{recent_pending_orders} new pending orders',
            'url': '/orders/?status=PENDING',
            'time': timezone.now()
        })
    
    return {
        'notifications': notifications,
        'notifications_count': len(notifications)
    }
