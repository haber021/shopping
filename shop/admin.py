from django.contrib import admin
from .models import (
    Category, Supplier, Product, Customer, 
    Order, OrderItem, InventoryTransaction, Setting
)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_person', 'email', 'phone')
    search_fields = ('name', 'contact_person', 'email')

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock', 'reorder_level', 'is_low_stock')
    list_filter = ('category', 'supplier')
    search_fields = ('name', 'description')

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'loyalty_points')
    search_fields = ('name', 'email', 'phone')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'status', 'order_date', 'total_amount')
    list_filter = ('status', 'order_date')
    search_fields = ('customer__name', 'id')
    inlines = [OrderItemInline]

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price', 'total')
    list_filter = ('order',)
    search_fields = ('order__id', 'product__name')

@admin.register(InventoryTransaction)
class InventoryTransactionAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity', 'transaction_type', 'transaction_date', 'reference')
    list_filter = ('transaction_type', 'transaction_date')
    search_fields = ('product__name', 'reference')

@admin.register(Setting)
class SettingAdmin(admin.ModelAdmin):
    list_display = ('key', 'value')
    search_fields = ('key',)
