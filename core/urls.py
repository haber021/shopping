from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views


urlpatterns = [
    # Authentication
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', views.register_view, name='register'),
    
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Products
    path('products/', views.ProductListView.as_view(), name='product-list'),
    path('products/<int:pk>/', views.ProductDetailView.as_view(), name='product-detail'),
    path('products/create/', views.ProductCreateView.as_view(), name='product-create'),
    path('products/<int:pk>/update/', views.ProductUpdateView.as_view(), name='product-update'),
    path('products/<int:pk>/delete/', views.ProductDeleteView.as_view(), name='product-delete'),
    
    # Orders
    path('orders/', views.OrderListView.as_view(), name='order-list'),
    path('orders/<int:pk>/', views.OrderDetailView.as_view(), name='order-detail'),
    path('orders/<int:pk>/update-status/', views.update_order_status, name='update-order-status'),
    
    # Inventory
    path('inventory/', views.InventoryListView.as_view(), name='inventory-list'),
    path('inventory/<int:pk>/restock/', views.restock_inventory, name='restock-inventory'),
    
    # Customers
    path('customers/', views.CustomerListView.as_view(), name='customer-list'),
    path('customers/<int:pk>/', views.CustomerDetailView.as_view(), name='customer-detail'),
    path('customers/create/', views.CustomerCreateView.as_view(), name='customer-create'),
    path('customers/<int:pk>/update/', views.CustomerUpdateView.as_view(), name='customer-update'),
    
    # Reports
    path('reports/', views.reports_view, name='reports'),
    
    # Settings
    path('settings/', views.settings_view, name='settings'),
    
    # HTMX endpoints
    path('htmx/products/<int:pk>/', views.htmx_product_detail, name='htmx-product-detail'),
    path('htmx/orders/<int:pk>/', views.htmx_order_detail, name='htmx-order-detail'),
    path('htmx/customers/<int:pk>/', views.htmx_customer_detail, name='htmx-customer-detail'),
    
    # API endpoints for charts
    path('api/sales-chart-data/', views.sales_chart_data, name='sales-chart-data'),
    path('api/inventory-chart-data/', views.inventory_chart_data, name='inventory-chart-data'),
]
