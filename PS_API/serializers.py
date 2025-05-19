from rest_framework import serializers
from PS.models import  ActivityLog, Notification
from core.models import Supplier, Product, Inventory, Order, OrderItem

class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    supplier_name = serializers.ReadOnlyField(source='supplier.name')
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'sku', 'description', 'category', 'supplier', 
                 'supplier_name', 'minimum_stock', 'price']

class ProductWithSupplierSerializer(serializers.ModelSerializer):
    supplier = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'sku', 'description', 'category', 'supplier', 
                 'minimum_stock', 'price']
        
    def get_supplier(self, obj):
        return {
            'id': obj.supplier.id,
            'name': obj.supplier.name
        }

class InventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventory
        fields = '__all__'

class InventoryWithProductSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    status = serializers.ReadOnlyField()
    
    class Meta:
        model = Inventory
        fields = ['id', 'product', 'current_stock', 'last_updated', 'status']

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')
    total_price = serializers.ReadOnlyField()
    
    class Meta:
        model = OrderItem
        fields = ['id', 'order', 'product', 'product_name', 'quantity', 'unit_price', 'total_price']

class OrderSerializer(serializers.ModelSerializer):
    supplier_name = serializers.ReadOnlyField(source='supplier.name')
    
    class Meta:
        model = Order
        fields = ['id', 'order_number', 'date', 'supplier', 'supplier_name', 
                 'status', 'expected_delivery', 'notes']

class OrderWithItemsSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    supplier_name = serializers.ReadOnlyField(source='supplier.name')
    
    class Meta:
        model = Order
        fields = ['id', 'order_number', 'date', 'supplier', 'supplier_name', 
                 'status', 'expected_delivery', 'notes', 'items']

class ActivityLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityLog
        fields = '__all__'

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'

class LowStockItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    sku = serializers.CharField()
    current_stock = serializers.IntegerField()
    minimum_stock = serializers.IntegerField()
    supplier = serializers.DictField()
    status = serializers.CharField()

class DashboardSummarySerializer(serializers.Serializer):
    total_products = serializers.IntegerField()
    active_suppliers = serializers.IntegerField()
    pending_orders = serializers.IntegerField()
    low_stock_items = serializers.IntegerField()