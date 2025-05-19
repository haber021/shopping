from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Supplier(models.Model):
    name = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=100, blank=True, null=True)
    delivery_time = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, default='active')
    
    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=255)
    sku = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=100, blank=True, null=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='products')
    minimum_stock = models.PositiveIntegerField(default=10)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.name} ({self.sku})"

class Inventory(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='inventory')
    current_stock = models.PositiveIntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.product.name} - {self.current_stock} in stock"
    
    @property
    def status(self):
        if self.current_stock <= 0:
            return 'critical'
        elif self.current_stock < self.product.minimum_stock:
            return 'low'
        else:
            return 'normal'

class Order(models.Model):
    ORDER_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    )
    
    order_number = models.CharField(max_length=50, unique=True)
    date = models.DateTimeField(default=timezone.now)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='pending')
    expected_delivery = models.DateTimeField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Order {self.order_number} - {self.status}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
    
    @property
    def total_price(self):
        return self.quantity * self.unit_price

class ActivityLog(models.Model):
    TYPE_CHOICES = (
        ('inventory-updated', 'Inventory Updated'),
        ('order-created', 'Order Created'),
        ('order-updated', 'Order Updated'),
        ('supplier-added', 'Supplier Added'),
        ('supplier-updated', 'Supplier Updated'),
        ('product-added', 'Product Added'),
        ('product-updated', 'Product Updated'),
        ('low-stock', 'Low Stock Alert'),
    )
    
    type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    description = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    entity_type = models.CharField(max_length=50, blank=True, null=True)
    entity_id = models.PositiveIntegerField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.type} - {self.timestamp}"
    
    class Meta:
        ordering = ['-timestamp']

class Notification(models.Model):
    TYPE_CHOICES = (
        ('low-stock', 'Low Stock Alert'),
        ('order-status', 'Order Status Update'),
        ('system', 'System Notification'),
    )
    
    type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    message = models.TextField()
    read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(default=timezone.now)
    entity_type = models.CharField(max_length=50, blank=True, null=True)
    entity_id = models.PositiveIntegerField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.type} - {'Read' if self.read else 'Unread'}"
    
    class Meta:
        ordering = ['-timestamp']
