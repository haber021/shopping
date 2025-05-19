from django.urls import path
from . import views

app_name = 'online_retail_dash'

urlpatterns = [
    path('online/', views.home, name='home'),
    path('online_dashboard/', views.dashboard, name='dashboard'),
    path('orders/', views.orders, name='orders'),
    path('inventory/', views.inventory, name='inventory'),
    path('procurement/', views.procurement, name='procurement'),
    path('crm/', views.crm, name='crm'),
    path('settings/', views.settings_view, name='settings'),
    path('help/', views.help_view, name='help'),
    path('search/', views.search, name='search'),
    path('profile/', views.profile, name='profile'),
    path('logout/', views.logout_view, name='logout'),
]