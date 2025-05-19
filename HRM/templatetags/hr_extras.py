
from django import template

register = template.Library()

@register.filter
def percentage_of(value, total):
    try:
        return round((float(value) / float(total)) * 100) if total > 0 else 0
    except (ValueError, ZeroDivisionError):
        return 0
