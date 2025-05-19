from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum
from rest_framework.decorators import api_view
from rest_framework.response import Response


from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Categories"

class Supplier(models.Model):
    name = models.CharField(max_length=100)
    contact_person = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    stock = models.PositiveIntegerField(default=0)
    reorder_level = models.PositiveIntegerField(default=10)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    @property
    def is_low_stock(self):
        return self.stock <= self.reorder_level
    
    def __str__(self):
        return self.name

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='customer')
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    loyalty_points = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('packed', 'Packed'),
        ('shipped', 'Shipped'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    )
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    order_date = models.DateTimeField(default=timezone.now)
    shipping_address = models.TextField()
    payment_method = models.CharField(max_length=50)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    tracking_number = models.CharField(max_length=100, blank=True, null=True)
    tracking_url = models.URLField(blank=True, null=True)
    delivery_partner = models.CharField(max_length=100, blank=True, null=True)
    estimated_delivery = models.DateField(blank=True, null=True)
    last_updated = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True, null=True)
    qr_code = models.ImageField(upload_to='order_qr_codes/', blank=True, null=True)
    
    def __str__(self):
        return f"Order #{self.id} - {self.customer.name}"
        
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        
        # First save the order
        super().save(*args, **kwargs)
        
        # Generate QR code for new orders
        if is_new or not self.qr_code:
            self.generate_qr_code()
            
    def generate_qr_code(self):
        import qrcode
        from django.core.files.base import ContentFile
        from io import BytesIO
        
        # Create QR code for order tracking
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        
        # The QR code will contain a URL to the order tracking page
        tracking_data = f"Order #{self.id}, Customer: {self.customer.name}, Status: {self.get_status_display()}"
        qr.add_data(tracking_data)
        qr.make(fit=True)
        
        # Create an image from the QR Code
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Save the QR code image
        buffer = BytesIO()
        img.save(buffer)
        filename = f'order_qr_{self.id}.png'
        
        # Save to the model's ImageField
        self.qr_code.save(filename, ContentFile(buffer.getvalue()), save=False)
        super().save(update_fields=['qr_code'])
        
    def get_latest_location(self):
        """Get the latest delivery location for this order"""
        location = self.delivery_locations.order_by('-timestamp').first()
        return location

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    @property
    def total(self):
        return self.price * self.quantity
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

class InventoryTransaction(models.Model):
    TRANSACTION_TYPES = (
        ('restock', 'Restock'),
        ('order', 'Order'),
        ('adjustment', 'Adjustment'),
    )
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='transactions')
    quantity = models.IntegerField()  # Positive for additions, negative for reductions
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    transaction_date = models.DateTimeField(default=timezone.now)
    reference = models.CharField(max_length=100, blank=True, null=True)  # Order number, supplier invoice, etc.
    notes = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.transaction_type} - {self.product.name} ({self.quantity})"

class DeliveryLocation(models.Model):
    """Model for tracking the physical location of an order during delivery"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='delivery_locations')
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    location_name = models.CharField(max_length=200, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    status_update = models.CharField(max_length=20, choices=Order.STATUS_CHOICES, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Location update for Order #{self.order.id} at {self.timestamp}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Update the order status if this location update includes a status change
        if self.status_update and self.order.status != self.status_update:
            self.order.status = self.status_update
            self.order.save(update_fields=['status'])
            
class OrderStatusHistory(models.Model):
    """Model for tracking status changes of an order"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='status_history')
    status = models.CharField(max_length=20, choices=Order.STATUS_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    location = models.ForeignKey(DeliveryLocation, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f"Order #{self.order.id} changed to {self.get_status_display()} at {self.timestamp}"
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name_plural = "Order status histories"

class Setting(models.Model):
    """Model for storing application settings"""
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField()
    
    def __str__(self):
        return self.key
        
class CustomerDashboardPreference(models.Model):
    """Model for storing customer dashboard preferences"""
    WIDGET_CHOICES = (
        ('recent_orders', 'Recent Orders'),
        ('order_status', 'Order Status'),
        ('loyalty_points', 'Loyalty Points'),
        ('saved_items', 'Saved Items'),
        ('recommended', 'Recommended Products'),
        ('recent_views', 'Recently Viewed'),
        ('promotions', 'Promotions'),
    )
    
    THEME_CHOICES = (
        ('light', 'Light'),
        ('dark', 'Dark'),
        ('blue', 'Blue'),
        ('green', 'Green'),
    )
    
    LAYOUT_CHOICES = (
        ('compact', 'Compact'),
        ('comfortable', 'Comfortable'),
        ('spacious', 'Spacious'),
    )
    
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE, related_name='dashboard_preference')
    active_widgets = models.JSONField(default=list)  # List of active widgets in display order
    widget_settings = models.JSONField(default=dict)  # Settings for each widget (size, position, etc.)
    theme = models.CharField(max_length=20, choices=THEME_CHOICES, default='light')
    layout = models.CharField(max_length=20, choices=LAYOUT_CHOICES, default='comfortable')
    show_welcome = models.BooleanField(default=True)  # Whether to show welcome message
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.customer.name}'s Dashboard Preferences"
    
    def get_active_widgets(self):
        """Returns the list of active widgets"""
        # If no widgets are set, return default widgets
        if not self.active_widgets:
            return ['recent_orders', 'loyalty_points', 'recommended']
        return self.active_widgets
    
    def get_widget_settings(self, widget_id):
        """Returns settings for a specific widget"""
        if not self.widget_settings or widget_id not in self.widget_settings:
            # Default settings if none are saved
            default_settings = {
                'size': 'medium',
                'position': 0,
                'collapsed': False,
                'max_items': 5
            }
            return default_settings
        return self.widget_settings.get(widget_id, {})
        
# Signals
@receiver(post_save, sender=Order)
def update_order_status_history(sender, instance, created, **kwargs):
    """
    Create a status history entry when an order is created or its status changes.
    This will ensure we maintain a complete history of all order status changes.
    """
    # Check if this is a new order or status has changed
    if created:
        OrderStatusHistory.objects.create(
            order=instance,
            status=instance.status,
            notes=f"Order created with status: {instance.get_status_display()}"
        )
    else:
        # Get the most recent status history
        latest_status = instance.status_history.first()
        
        # If the status has changed from the most recent entry, create a new one
        if not latest_status or latest_status.status != instance.status:
            OrderStatusHistory.objects.create(
                order=instance,
                status=instance.status,
                notes=f"Status updated to: {instance.get_status_display()}"
            )
