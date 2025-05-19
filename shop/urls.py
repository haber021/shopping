from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Products
    path('products/', views.product_list, name='product_list'),
    path('products/create/', views.product_create, name='product_create'),
    path('products/<int:pk>/', views.product_detail, name='product_detail'),
    path('products/<int:pk>/edit/', views.product_edit, name='product_edit'),
    path('products/<int:pk>/delete/', views.product_delete, name='product_delete'),
    
    # Orders
    path('orders/', views.order_list, name='order_list'),
    path('orders/create/', views.order_create, name='order_create'),
    path('orders/<int:pk>/', views.order_detail, name='order_detail'),
    path('orders/<int:pk>/update/', views.order_update, name='order_update'),
    path('orders/<int:pk>/cancel/', views.order_cancel, name='order_cancel'),
    
    # Inventory
    path('inventory/', views.inventory_list, name='inventory_list'),
    path('inventory/restock/<int:product_id>/', views.inventory_restock, name='inventory_restock'),
    
    # Customers
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/create/', views.customer_create, name='customer_create'),
    path('customers/<int:pk>/', views.customer_detail, name='customer_detail'),
    path('customers/<int:pk>/edit/', views.customer_edit, name='customer_edit'),
    
    # Suppliers
    path('suppliers/', views.supplier_list, name='supplier_list'),
    path('suppliers/create/', views.supplier_create, name='supplier_create'),
    path('suppliers/<int:pk>/', views.supplier_detail, name='supplier_detail'),
    path('suppliers/<int:pk>/edit/', views.supplier_edit, name='supplier_edit'),
    
    # Reports
    path('reports/', views.report_index, name='report_index'),
    path('reports/sales/', views.sales_report, name='sales_report'),
    path('reports/inventory/', views.inventory_report, name='inventory_report'),
    path('reports/customers/', views.customers_report, name='customers_report'),
    
    # Settings
    path('settings/general/', views.settings_general, name='settings_general'),
    path('settings/payment/', views.settings_payment, name='settings_payment'),
    path('settings/shipping/', views.settings_shipping, name='settings_shipping'),
    path('settings/users/', views.settings_users, name='settings_users'),
    path('settings/users/create/', views.user_create, name='user_create'),
    path('settings/users/<int:pk>/edit/', views.user_edit, name='user_edit'),
    
    # API endpoints for HTMX and Charts
    path('api/dashboard/stats/', views.api_dashboard_stats, name='api_dashboard_stats'),
    path('api/dashboard/sales-chart/', views.api_sales_chart, name='api_sales_chart'),
    path('api/dashboard/inventory-chart/', views.api_inventory_chart, name='api_inventory_chart'),
    
    path('api/dashboard/sales-chart/', views.api_sales_chart, name='api_sales_chart'),
    path('api/dashboard/inventory-chart/', views.api_inventory_chart, name='api_inventory_chart'),
]
