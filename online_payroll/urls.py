from django.urls import path
from . import views

app_name = 'payroll'

urlpatterns = [
    path('employees/', views.employee_list, name='employee_list'),
    path('employees/<int:pk>/', views.employee_detail, name='employee_detail'),
    path('employees/add/', views.add_employee, name='add_employee'),
    path('employees/edit/<int:pk>/', views.edit_employee, name='edit_employee'),
    path('pay-heads/', views.pay_heads, name='pay_heads'),
    path('pay-heads/edit/<int:pk>/', views.edit_pay_head, name='edit_pay_head'),
    path('salary-slip/<int:pk>/', views.salary_slip, name='salary_slip'),
    path('run-payroll/', views.run_payroll, name='run_payroll'),
    path('payroll-list/', views.payroll_list, name='payroll_list'),
]
