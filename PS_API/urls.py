from django.urls import path
from . import views

app_name = 'PS_API'

urlpatterns = [
    # Auth routes
    path('auth/login/', views.login_view, name='login'),
    
    # Dashboard routes
    path('dashboard/summary/', views.dashboard_summary, name='dashboard_summary'),
    path('dashboard/low-stock/', views.low_stock, name='low_stock'),
    path('dashboard/recent-activity/', views.recent_activity, name='recent_activity'),
    
    # Supplier routes
    path('suppliers/', views.supplier_list, name='supplier_list'),
    path('suppliers/<int:pk>/', views.supplier_detail, name='supplier_detail'),
    path('suppliers/create/', views.supplier_create, name='supplier_create'),
    
    # Product routes
    path('products/', views.product_list, name='product_list'),
    path('products/<int:pk>/', views.product_detail, name='product_detail'),
    path('products/create/', views.product_create, name='product_create'),
    
    # Inventory routes
    path('inventory/', views.inventory_list, name='inventory_list'),
    path('inventory/products/<int:product_id>/', views.inventory_by_product, name='inventory_by_product'),
    path('inventory/update/', views.inventory_update, name='inventory_update'),
    
    # Order routes
    path('orders/', views.order_list, name='order_list'),
    path('orders/<int:pk>/', views.order_detail, name='order_detail'),
    path('orders/create/', views.order_create, name='order_create'),
    
    # Notification routes
    path('notifications/unread/', views.unread_notifications, name='unread_notifications'),
    path('notifications/<int:pk>/read/', views.mark_notification_read, name='mark_notification_read'),
]