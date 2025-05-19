from django.contrib import admin
from .models import (
    Supplier, 
    Product, 
    Inventory, 
    Order, 
    OrderItem, 
    ActivityLog, 
    Notification
)

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_person', 'phone', 'email', 'status')
    search_fields = ('name', 'contact_person', 'email')
    list_filter = ('status', 'category')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'sku', 'category', 'supplier', 'price', 'minimum_stock')
    search_fields = ('name', 'sku', 'description')
    list_filter = ('category', 'supplier')

@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ('product', 'current_stock', 'status', 'last_updated')
    search_fields = ('product__name', 'product__sku')
    list_filter = ('last_updated',)
    readonly_fields = ('last_updated',)

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'supplier', 'status', 'date', 'expected_delivery')
    search_fields = ('order_number', 'supplier__name')
    list_filter = ('status', 'date')
    inlines = [OrderItemInline]

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'unit_price', 'total_price')
    list_filter = ('order', 'product')

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('type', 'description', 'timestamp', 'entity_type', 'entity_id')
    list_filter = ('type', 'timestamp', 'entity_type')
    readonly_fields = ('timestamp',)

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('type', 'message', 'read', 'timestamp', 'entity_type', 'entity_id')
    list_filter = ('type', 'read', 'timestamp')
    readonly_fields = ('timestamp',)
