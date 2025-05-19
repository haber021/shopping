from django.urls import path
from . import views

app_name = 'hr'

urlpatterns = [
    # Employee management
    path('employees/', views.employee_list, name='employees'),
    path('employees/add/', views.employee_add, name='employee_add'),
    path('employees/<int:employee_id>/', views.employee_detail, name='employee_detail'),
    path('employees/<int:employee_id>/edit/', views.employee_edit, name='employee_edit'),
    path('employees/<int:employee_id>/delete/', views.employee_delete, name='employee_delete'),
    
    # Departments and positions
    path('departments/', views.department_list, name='departments'),
    path('positions/', views.position_list, name='positions'),
    
    # Attendance
    path('attendance/', views.attendance, name='attendance'),
    path('attendance/add/', views.attendance_add, name='attendance_add'),
    path('attendance/bulk/', views.attendance_bulk, name='attendance_bulk'),
    
    # Scheduling
    path('schedule/', views.schedule, name='schedule'),
    path('schedule/add/', views.schedule_add, name='schedule_add'),
    path('schedule/bulk/', views.schedule_bulk, name='schedule_bulk'),
    
    # Leave management
    path('leave/', views.leave, name='leave'),
    path('leave/add/', views.leave_add, name='leave_add'),
    path('leave/<int:leave_id>/approve/', views.leave_approve, name='leave_approve'),
    
    # Recruitment
    path('recruitment/', views.recruitment, name='recruitment'),
    path('recruitment/add/', views.recruitment_add, name='recruitment_add'),
    path('recruitment/<int:application_id>/', views.recruitment_detail, name='recruitment_detail'),
    
    # Documents
    path('documents/', views.documents, name='documents'),
    path('documents/add/', views.document_add, name='document_add'),
    path('documents/<int:document_id>/delete/', views.document_delete, name='document_delete'),
]