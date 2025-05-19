from django.contrib import admin
from .models import Product, Category, Customer, Order, OrderItem, Supplier, Inventory

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('name', 'description')
    date_hierarchy = 'created_at'

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'created_at')
    search_fields = ('name', 'email', 'phone')
    date_hierarchy = 'created_at'

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'status', 'created_at', 'total_amount')
    list_filter = ('status', 'created_at')
    search_fields = ('customer__name', 'shipping_address')
    date_hierarchy = 'created_at'
    inlines = [OrderItemInline]

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_person', 'email', 'phone')
    search_fields = ('name', 'contact_person', 'email')

@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ('product', 'current_stock', 'reorder_level', 'last_updated')
    list_filter = ('last_updated',)
    search_fields = ('product__name',)
    date_hierarchy = 'last_updated'
