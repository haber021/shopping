from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from django.db.models import Count, Q

from PS.models import ActivityLog, Notification

from core.models import (
    Supplier,
    Product,
    Inventory,
    Order,
)
from .serializers import (
    SupplierSerializer,
    ProductSerializer,
    ProductWithSupplierSerializer,
    InventorySerializer,
    InventoryWithProductSerializer,
    OrderSerializer,
    OrderWithItemsSerializer,
    OrderItemSerializer,
    ActivityLogSerializer,
    NotificationSerializer,
    LowStockItemSerializer,
    DashboardSummarySerializer
)

# Authentication views
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')
    
    user = authenticate(username=username, password=password)
    
    if user:
        return Response({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.is_staff and 'admin' or 'user'
        })
    else:
        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )

# Dashboard views
@api_view(['GET'])
def dashboard_summary(request):
    total_products = Product.objects.count()
    active_suppliers = Supplier.objects.filter(status='active').count()
    pending_orders = Order.objects.filter(status='pending').count()
    
    # Count low stock items
    low_stock_items = 0
    inventory_items = Inventory.objects.select_related('product').all()
    for inv in inventory_items:
        if inv.current_stock < inv.product.minimum_stock:
            low_stock_items += 1
    
    data = {
        'total_products': total_products,
        'active_suppliers': active_suppliers,
        'pending_orders': pending_orders,
        'low_stock_items': low_stock_items
    }
    
    serializer = DashboardSummarySerializer(data)
    return Response(serializer.data)

@api_view(['GET'])
def low_stock(request):
    low_stock_items = []
    inventory_items = Inventory.objects.select_related('product__supplier').all()
    
    for inv in inventory_items:
        if inv.current_stock < inv.product.minimum_stock:
            item = {
                'id': inv.product.id,
                'name': inv.product.name,
                'sku': inv.product.sku,
                'current_stock': inv.current_stock,
                'minimum_stock': inv.product.minimum_stock,
                'supplier': {
                    'id': inv.product.supplier.id,
                    'name': inv.product.supplier.name
                },
                'status': inv.status
            }
            low_stock_items.append(item)
    
    serializer = LowStockItemSerializer(low_stock_items, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def recent_activity(request):
    activities = ActivityLog.objects.all().order_by('-timestamp')[:10]
    serializer = ActivityLogSerializer(activities, many=True)
    return Response(serializer.data)

# Supplier views
@api_view(['GET'])
def supplier_list(request):
    suppliers = Supplier.objects.all()
    serializer = SupplierSerializer(suppliers, many=True)
    return Response(serializer.data)

@api_view(['GET', 'PUT', 'DELETE'])
def supplier_detail(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    
    if request.method == 'GET':
        serializer = SupplierSerializer(supplier)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = SupplierSerializer(supplier, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            
            # Log the activity
            ActivityLog.objects.create(
                type='supplier-updated',
                description=f"Supplier {supplier.name} was updated",
                entity_type='supplier',
                entity_id=supplier.id
            )
            
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        supplier_name = supplier.name
        supplier.delete()
        
        # Log the activity
        ActivityLog.objects.create(
            type='supplier-deleted',
            description=f"Supplier {supplier_name} was deleted",
            entity_type='supplier',
            entity_id=pk
        )
        
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
def supplier_create(request):
    serializer = SupplierSerializer(data=request.data)
    if serializer.is_valid():
        supplier = serializer.save()
        
        # Log the activity
        ActivityLog.objects.create(
            type='supplier-added',
            description=f"New supplier {supplier.name} was added",
            entity_type='supplier',
            entity_id=supplier.id
        )
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Product views
@api_view(['GET'])
def product_list(request):
    products = Product.objects.all()
    serializer = ProductWithSupplierSerializer(products, many=True)
    return Response(serializer.data)

@api_view(['GET', 'PUT', 'DELETE'])
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    
    if request.method == 'GET':
        serializer = ProductWithSupplierSerializer(product)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = ProductSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            updated_product = serializer.save()
            
            # Log the activity
            ActivityLog.objects.create(
                type='product-updated',
                description=f"Product {updated_product.name} was updated",
                entity_type='product',
                entity_id=updated_product.id
            )
            
            return Response(ProductWithSupplierSerializer(updated_product).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        product_name = product.name
        product.delete()
        
        # Log the activity
        ActivityLog.objects.create(
            type='product-deleted',
            description=f"Product {product_name} was deleted",
            entity_type='product',
            entity_id=pk
        )
        
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
def product_create(request):
    serializer = ProductSerializer(data=request.data)
    if serializer.is_valid():
        product = serializer.save()
        
        # Automatically create inventory entry for new product
        Inventory.objects.create(product=product, current_stock=0)
        
        # Log the activity
        ActivityLog.objects.create(
            type='product-added',
            description=f"New product {product.name} was added",
            entity_type='product',
            entity_id=product.id
        )
        
        return Response(ProductWithSupplierSerializer(product).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Inventory views
@api_view(['GET'])
def inventory_list(request):
    inventory = Inventory.objects.select_related('product').all()
    serializer = InventoryWithProductSerializer(inventory, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def inventory_by_product(request, product_id):
    inventory = get_object_or_404(Inventory, product_id=product_id)
    serializer = InventoryWithProductSerializer(inventory)
    return Response(serializer.data)

@api_view(['PUT'])
def inventory_update(request):
    product_id = request.data.get('productId')
    quantity = request.data.get('quantity')
    
    if not product_id or quantity is None:
        return Response(
            {'error': 'Both productId and quantity are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    inventory = get_object_or_404(Inventory, product_id=product_id)
    inventory.current_stock = quantity
    inventory.save()
    
    # Log the activity
    ActivityLog.objects.create(
        type='inventory-updated',
        description=f"Inventory for {inventory.product.name} updated to {quantity} units",
        entity_type='inventory',
        entity_id=inventory.id
    )
    
    # Check if stock is low and create notification if needed
    if inventory.status in ['critical', 'low']:
        Notification.objects.create(
            type='low-stock',
            message=f"{inventory.product.name} is running low ({inventory.current_stock} units left)",
            entity_type='product',
            entity_id=product_id
        )
    
    serializer = InventoryWithProductSerializer(inventory)
    return Response(serializer.data)

# Order views
@api_view(['GET'])
def order_list(request):
    orders = Order.objects.select_related('supplier').all()
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)

@api_view(['GET', 'PUT'])
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    
    if request.method == 'GET':
        serializer = OrderWithItemsSerializer(order)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = OrderSerializer(order, data=request.data, partial=True)
        if serializer.is_valid():
            updated_order = serializer.save()
            
            # Log the activity
            ActivityLog.objects.create(
                type='order-updated',
                description=f"Order {updated_order.order_number} status changed to {updated_order.status}",
                entity_type='order',
                entity_id=updated_order.id
            )
            
            # Create notification for status change
            Notification.objects.create(
                type='order-status',
                message=f"Order {updated_order.order_number} status changed to {updated_order.status}",
                entity_type='order',
                entity_id=updated_order.id
            )
            
            return Response(OrderWithItemsSerializer(updated_order).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def order_create(request):
    order_data = {
        'order_number': request.data.get('orderNumber'),
        'supplier': request.data.get('supplierId'),
        'status': request.data.get('status', 'pending'),
        'expected_delivery': request.data.get('expectedDelivery'),
        'notes': request.data.get('notes')
    }
    
    order_serializer = OrderSerializer(data=order_data)
    if order_serializer.is_valid():
        order = order_serializer.save()
        
        # Process order items
        order_items = request.data.get('items', [])
        for item_data in order_items:
            item = {
                'order': order.id,
                'product': item_data.get('productId'),
                'quantity': item_data.get('quantity'),
                'unit_price': item_data.get('unitPrice')
            }
            item_serializer = OrderItemSerializer(data=item)
            if item_serializer.is_valid():
                item_serializer.save()
            else:
                # Rollback the order if items are invalid
                order.delete()
                return Response(item_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Log the activity
        ActivityLog.objects.create(
            type='order-created',
            description=f"New order {order.order_number} was created",
            entity_type='order',
            entity_id=order.id
        )
        
        # Notification for new order
        Notification.objects.create(
            type='order-status',
            message=f"New order {order.order_number} was created with status {order.status}",
            entity_type='order',
            entity_id=order.id
        )
        
        return Response(OrderWithItemsSerializer(order).data, status=status.HTTP_201_CREATED)
    return Response(order_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Notification views
@api_view(['GET'])
def unread_notifications(request):
    notifications = Notification.objects.filter(read=False)
    serializer = NotificationSerializer(notifications, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def mark_notification_read(request, pk):
    notification = get_object_or_404(Notification, pk=pk)
    notification.read = True
    notification.save()
    return Response({'success': True})
