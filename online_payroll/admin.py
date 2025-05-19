from django.contrib import admin
from .models import (
    Department, PayHead, Employee, EmployeePayHead,
    Payroll, SalarySlip, SalarySlipDetail
)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name', 'code')


@admin.register(PayHead)
class PayHeadAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'is_active')
    list_filter = ('type', 'is_active')
    search_fields = ('name', 'description')


class EmployeePayHeadInline(admin.TabularInline):
    model = EmployeePayHead
    extra = 1


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('employee_id', 'last_name', 'first_name', 'department', 'employment_type', 'base_salary', 'active')
    list_filter = ('department', 'employment_type', 'active', 'join_date')
    search_fields = ('employee_id', 'first_name', 'last_name', 'email')
    inlines = [EmployeePayHeadInline]


class SalarySlipDetailInline(admin.TabularInline):
    model = SalarySlipDetail
    extra = 1


@admin.register(SalarySlip)
class SalarySlipAdmin(admin.ModelAdmin):
    list_display = ('id', 'employee', 'payroll', 'basic_salary', 'total_earnings', 'total_deductions', 'net_salary')
    list_filter = ('payroll', 'created_at')
    search_fields = ('employee__first_name', 'employee__last_name', 'employee__employee_id')
    inlines = [SalarySlipDetailInline]


@admin.register(Payroll)
class PayrollAdmin(admin.ModelAdmin):
    list_display = ('id', 'description', 'start_date', 'end_date', 'processed_at')
    list_filter = ('start_date', 'end_date')
    search_fields = ('description',)
