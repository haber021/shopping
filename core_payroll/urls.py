# core_payroll/urls.py
from django.urls import path
from . import views

app_name = 'core_payroll'  # Make sure this is present

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('demo-login/', views.demo_login, name='demo_login_payroll'),
    # other URL patterns for this app
]
