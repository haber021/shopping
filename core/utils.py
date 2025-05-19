from django.db.models import Sum, F
from django.utils import timezone
from datetime import timedelta

from .models import Order, OrderItem, Inventory, Product


def get_low_stock_products():
    """Returns a queryset of products with low stock levels"""
    return Inventory.objects.filter(
        current_stock__lte=F('reorder_level')
    ).select_related('product')


def get_out_of_stock_products():
    """Returns a queryset of products that are out of stock"""
    return Inventory.objects.filter(
        current_stock=0
    ).select_related('product')


def get_revenue_for_period(days=30):
    """Calculate revenue for the specified number of days"""
    start_date = timezone.now() - timedelta(days=days)
    
    revenue = OrderItem.objects.filter(
        order__created_at__gte=start_date
    ).aggregate(
        total=Sum(F('price') * F('quantity'))
    )['total'] or 0
    
    return revenue


def get_sales_trend_data(days=30):
    """Get sales trend data for the specified number of days"""
    start_date = timezone.now() - timedelta(days=days)
    
    orders_by_day = Order.objects.filter(
        created_at__gte=start_date
    ).values('created_at__date').annotate(
        total=Sum(F('items__price') * F('items__quantity')),
        count=Sum('items__quantity')
    ).order_by('created_at__date')
    
    return orders_by_day


def get_top_selling_products(days=30, limit=5):
    """Get the top selling products for the specified number of days"""
    start_date = timezone.now() - timedelta(days=days)
    
    top_products = OrderItem.objects.filter(
        order__created_at__gte=start_date
    ).values('product__name').annotate(
        total_sold=Sum('quantity'),
        revenue=Sum(F('price') * F('quantity'))
    ).order_by('-total_sold')[:limit]
    
    return top_products


def get_total_inventory_value():
    """Calculate the total value of current inventory"""
    inventory_items = Inventory.objects.select_related('product').all()
    total_value = sum(item.current_stock * item.product.price for item in inventory_items)
    return total_value


def process_order(order, create_transaction=True):
    """Process an order by updating inventory levels"""
    for item in order.items.all():
        # Get inventory for the product
        inventory, created = Inventory.objects.get_or_create(
            product=item.product,
            defaults={'current_stock': 0, 'reorder_level': 10}
        )
        
        # Reduce inventory
        if inventory.current_stock >= item.quantity:
            inventory.current_stock -= item.quantity
            inventory.save()
            
            # Create transaction record if requested
            if create_transaction:
                from .models import InventoryTransaction
                InventoryTransaction.objects.create(
                    inventory=inventory,
                    quantity=-item.quantity,
                    transaction_type='OUT',
                    reference=f"Order #{order.id}"
                )
        else:
            # Handle insufficient inventory
            return False
    
    return True
