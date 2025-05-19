from django.urls import path
from . import views

app_name = 'ps'
urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('suppliers/', views.suppliers, name='suppliers'),
    path('products/', views.products, name='products'), 
    path('inventory/', views.inventory, name='inventory'),
    path('orders/', views.orders, name='orders'),
]