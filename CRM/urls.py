# urls.py
from django.urls import path
from . import views

app_name = 'CRM'

urlpatterns = [
    # Authentication
    path('index/', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Contacts
    path('contacts/', views.contacts, name='contacts'),
    path('contacts/new/', views.new_contact, name='new_contact'),
    path('contacts/<int:contact_id>/', views.edit_contact, name='edit_contact'),
    path('contacts/<int:contact_id>/delete/', views.delete_contact, name='delete_contact'),
    
    # Leads
    path('leads/', views.leads, name='leads'),
    path('leads/new/', views.new_lead, name='new_lead'),
    path('leads/<int:lead_id>/edit/', views.edit_lead, name='edit_lead'),
    path('leads/<int:lead_id>/delete/', views.delete_lead, name='delete_lead'),
    path('leads/<int:lead_id>/update-stage/', views.update_lead_stage, name='update_lead_stage'),
    
    # Tasks
    path('tasks/', views.tasks, name='tasks'),
    path('tasks/new/', views.new_task, name='new_task'),
    path('tasks/<int:task_id>/edit/', views.edit_task, name='edit_task'),
    path('tasks/<int:task_id>/toggle-status/', views.toggle_task_status, name='toggle_task_status'),
    path('tasks/<int:task_id>/delete/', views.delete_task, name='delete_task'),
    
    # Reports
    path('reports/', views.reports, name='reports'),
    
    # Settings
    path('settings/', views.settings, name='settings'),
    
    # Activities
    path('activity/log/', views.log_activity, name='log_activity'),
    
    # API Endpoints
    path('api/contacts/', views.api_contacts, name='api_contacts'),
    path('api/leads/', views.api_leads, name='api_leads'),
    path('api/tasks/calendar/', views.api_calendar_tasks, name='api_calendar_tasks'),
    
]