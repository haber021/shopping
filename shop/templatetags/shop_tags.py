from django import template
from django.utils.safestring import mark_safe
from ..models import Product, Order

register = template.Library()

@register.simple_tag
def order_status_badge(status):
    """
    Returns a Bootstrap badge with appropriate color for the order status
    """
    badge_classes = {
        'pending': 'bg-warning',
        'processing': 'bg-info',
        'shipped': 'bg-primary',
        'delivered': 'bg-success',
        'cancelled': 'bg-danger'
    }
    
    badge_class = badge_classes.get(status, 'bg-secondary')
    return mark_safe(f'<span class="badge {badge_class}">{status.title()}</span>')

@register.simple_tag
def low_stock_badge(product):
    """
    Returns a badge indicating stock status
    """
    if product.stock <= 0:
        return mark_safe('<span class="badge bg-danger">Out of Stock</span>')
    elif product.stock <= product.reorder_level:
        return mark_safe('<span class="badge bg-warning">Low Stock</span>')
    return ''

@register.simple_tag
def get_total_value(product):
    """
    Calculate the total value of a product (price * stock)
    """
    return product.price * product.stock

@register.filter
def currency(value):
    """
    Format a value as currency
    """
    try:
        return f"${value:.2f}"
    except (ValueError, TypeError):
        return "$0.00"
