from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Categories"

class Supplier(models.Model):
    name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, related_name='products')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    @property
    def current_stock(self):
        inventory = self.inventory_set.first()
        if inventory:
            return inventory.current_stock
        return 0

class Inventory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    current_stock = models.PositiveIntegerField(default=0)
    reorder_level = models.PositiveIntegerField(default=10)
    last_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.product.name} - {self.current_stock} units"
    
    @property
    def is_low_stock(self):
        return self.current_stock <= self.reorder_level
    
    @property
    def is_out_of_stock(self):
        return self.current_stock == 0
    
    class Meta:
        verbose_name_plural = "Inventory"

class InventoryTransaction(models.Model):
    TRANSACTION_TYPES = (
        ('IN', 'Incoming'),
        ('OUT', 'Outgoing'),
        ('ADJ', 'Adjustment'),
    )
    
    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE, related_name='transactions')
    quantity = models.IntegerField()  # Can be positive or negative
    transaction_type = models.CharField(max_length=3, choices=TRANSACTION_TYPES)
    reference = models.CharField(max_length=100, blank=True, null=True)  # Order number, supplier invoice, etc.
    timestamp = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.transaction_type} - {self.quantity} units of {self.inventory.product.name}"

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='core_customer')
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    loyalty_points = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    @property
    def total_orders(self):
        return self.orders.count()

class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20)

    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('SHIPPED', 'Shipped'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    )
    
    PAYMENT_METHOD_CHOICES = (
        ('CREDIT_CARD', 'Credit Card'),
        ('DEBIT_CARD', 'Debit Card'),
        ('BANK_TRANSFER', 'Bank Transfer'),
        ('CASH_ON_DELIVERY', 'Cash on Delivery'),
    )
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders')
    order_number = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    tracking_number = models.CharField(max_length=100, blank=True, null=True)
    delivery_partner = models.CharField(max_length=100, blank=True, null=True)
    delivery_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def generate_order_number(self):
        """Generate a unique order number"""
        return f'ORD-{timezone.now().strftime("%Y%m%d")}-{self.pk:04d}'
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            super().save(*args, **kwargs)  # First save to get PK
            self.order_number = self.generate_order_number()
        super().save(*args, **kwargs)
    
    def mark_as_processing(self):
        self.status = 'PROCESSING'
        self.save()
        
    def mark_as_shipped(self, tracking_number, delivery_partner):
        self.status = 'SHIPPED'
        self.tracking_number = tracking_number
        self.delivery_partner = delivery_partner
        self.save()
        
    def mark_as_delivered(self):
        self.status = 'DELIVERED'
        self.save()
        
    def mark_as_completed(self):
        self.status = 'COMPLETED'
        self.save()
        
    def mark_as_cancelled(self):
        self.status = 'CANCELLED'
        self.save()
    
    @property
    def total_amount(self):
        return sum(item.total_price for item in self.items.all())
    
    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)  # price per item
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
    
    @property
    def total_price(self):
        return self.price * self.quantity

class CompanySettings(models.Model):
    company_name = models.CharField(max_length=200)
    logo = models.CharField(max_length=255, blank=True, null=True)  # URL to logo
    address = models.TextField()
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    def __str__(self):
        return self.company_name
    
    class Meta:
        verbose_name_plural = "Company Settings"
