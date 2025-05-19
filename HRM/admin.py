from django.contrib import admin
from .models import Department, Position, Employee, Attendance, Schedule, Leave, JobApplication, EmployeeDocument

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'manager')
    search_fields = ('name',)

@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ('title', 'department', 'min_salary', 'max_salary')
    list_filter = ('department',)
    search_fields = ('title', 'department__name')

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('employee_id', 'first_name', 'last_name', 'department', 'position', 'status')
    list_filter = ('department', 'status')
    search_fields = ('employee_id', 'first_name', 'last_name', 'email')
    fieldsets = (
        ('Personal Information', {
            'fields': ('employee_id', 'first_name', 'last_name', 'email', 'phone', 'gender', 'date_of_birth', 'address')
        }),
        ('Employment Information', {
            'fields': ('hire_date', 'department', 'position', 'manager', 'status')
        }),
        ('Emergency Contact', {
            'fields': ('emergency_contact_name', 'emergency_contact_phone')
        }),
        ('User Account', {
            'fields': ('user',)
        }),
    )

@admin.register(EmployeeDocument)
class EmployeeDocumentAdmin(admin.ModelAdmin):
    list_display = ('employee', 'document_type', 'title', 'upload_date', 'expiry_date')
    list_filter = ('document_type', 'upload_date')
    search_fields = ('employee__first_name', 'employee__last_name', 'title')

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date', 'status', 'time_in', 'time_out')
    list_filter = ('date', 'status')
    search_fields = ('employee__first_name', 'employee__last_name')
    date_hierarchy = 'date'

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date', 'shift_type', 'start_time', 'end_time')
    list_filter = ('date', 'shift_type')
    search_fields = ('employee__first_name', 'employee__last_name')
    date_hierarchy = 'date'

@admin.register(Leave)
class LeaveAdmin(admin.ModelAdmin):
    list_display = ('employee', 'leave_type', 'start_date', 'end_date', 'status')
    list_filter = ('leave_type', 'status', 'start_date')
    search_fields = ('employee__first_name', 'employee__last_name')
    date_hierarchy = 'start_date'

@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ('applicant_name', 'position', 'application_date', 'status')
    list_filter = ('status', 'position', 'application_date')
    search_fields = ('applicant_name', 'email', 'position__title')
    date_hierarchy = 'application_date'