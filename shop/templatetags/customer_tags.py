from django import template
from decimal import Decimal

register = template.Library()

@register.filter
def mul(value, arg):
    """Multiply the value by the argument"""
    try:
        return Decimal(str(value)) * Decimal(str(arg))
    except (ValueError, TypeError):
        return 0

@register.filter
def currency(value):
    """Format a value as currency"""
    try:
        return "${:.2f}".format(Decimal(str(value)))
    except (ValueError, TypeError):
        return "$0.00"

@register.filter
def subtotal(cart):
    """Calculate subtotal for all items in the cart"""
    if not cart:
        return 0
    
    return sum(Decimal(str(item['price'])) * item['quantity'] for item in cart)