from django.urls import path
from . import views

app_name = 'hr_dashboard'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
]