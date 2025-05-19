from django.urls import path
from . import customer_views

app_name = 'customer'

urlpatterns = [
    # Home and browsing
    path('', customer_views.home, name='home'),
    path('products/', customer_views.product_list, name='product_list'),
    path('products/<int:pk>/', customer_views.product_detail, name='product_detail'),
    path('category/<int:category_id>/', customer_views.product_by_category, name='product_by_category'),
    
    # Cart and checkout
    path('cart/', customer_views.cart_view, name='cart'),
    path('cart/add/<int:product_id>/', customer_views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/', customer_views.update_cart, name='update_cart'),
    path('cart/remove/<int:item_id>/', customer_views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', customer_views.checkout, name='checkout'),
    path('confirm-order/', customer_views.confirm_order, name='confirm_order'),
    path('order-success/<int:order_id>/', customer_views.order_success, name='order_success'),
    
    # User authentication
    path('register/', customer_views.register, name='register'),
    path('login/', customer_views.login_view, name='login'),
    path('logout/', customer_views.logout_view, name='logout'),
    
    # User account
    path('profile/', customer_views.profile, name='profile'),
    path('orders/', customer_views.order_history, name='order_history'),
    path('orders/<int:order_id>/', customer_views.order_detail, name='order_detail'),
    
    # Order tracking and QR code scanning
    path('orders/<int:order_id>/tracking/', customer_views.order_tracking, name='order_tracking'),
    path('scan/', customer_views.scan_qr_code, name='scan_qr_code'),
    path('scan/<int:order_id>/', customer_views.scan_qr_code, name='scan_qr_code_with_id'),
    path('orders/<int:order_id>/update-status/', customer_views.update_order_status, name='update_order_status'),
]