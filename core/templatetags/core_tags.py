from django import template
from django.utils import timezone
from datetime import timedelta

from core.models import Order, Product, Customer, Inventory

register = template.Library()

@register.simple_tag
def recent_orders(days=7, limit=5):
    """Returns recent orders within the specified number of days"""
    start_date = timezone.now() - timedelta(days=days)
    return Order.objects.filter(created_at__gte=start_date).order_by('-created_at')[:limit]

@register.simple_tag
def low_stock_products(limit=5):
    """Returns products with low stock"""
    return Inventory.objects.filter(
        current_stock__lte=F('reorder_level')
    ).select_related('product').order_by('current_stock')[:limit]

@register.simple_tag
def total_customers():
    """Returns the total number of customers"""
    return Customer.objects.count()

@register.simple_tag
def total_products():
    """Returns the total number of products"""
    return Product.objects.count()

@register.simple_tag
def total_orders():
    """Returns the total number of orders"""
    return Order.objects.count()

@register.simple_tag
def pending_orders():
    """Returns the number of pending orders"""
    return Order.objects.filter(status='PENDING').count()

@register.filter
def currency(value):
    """Format a number as currency"""
    return f"${value:.2f}"

@register.filter
def percentage(value, total):
    """Calculate percentage"""
    if total == 0:
        return "0%"
    return f"{(value / total) * 100:.1f}%"

@register.filter
def get_item(dictionary, key):
    """Get an item from a dictionary by key"""
    return dictionary.get(key)

@register.filter
def status_badge_class(status):
    """Returns the appropriate Bootstrap badge class based on order status"""
    status_classes = {
        'PENDING': 'badge-warning',
        'PROCESSING': 'badge-info',
        'SHIPPED': 'badge-primary',
        'DELIVERED': 'badge-success',
        'CANCELLED': 'badge-danger',
    }
    return status_classes.get(status, 'badge-secondary')

@register.filter
def stock_status_class(inventory):
    """Returns the appropriate Bootstrap text class based on inventory level"""
    if inventory.is_out_of_stock:
        return 'text-danger'
    elif inventory.is_low_stock:
        return 'text-warning'
    return 'text-success'
