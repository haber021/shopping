from django import forms
from .models import (
    Employee, Department, PayHead, EmployeePayHead, Payroll
)


class EmployeeForm(forms.ModelForm):
    """
    Form for creating and updating employees
    """
    class Meta:
        model = Employee
        fields = ['employee_id', 'first_name', 'last_name', 'department', 
                  'employment_type', 'join_date', 'base_salary', 'email', 
                  'phone', 'address', 'bank_name', 'bank_account', 'active']
        widgets = {
            'join_date': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }


class DepartmentForm(forms.ModelForm):
    """
    Form for creating and updating departments
    """
    class Meta:
        model = Department
        fields = ['name', 'code', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class PayHeadForm(forms.ModelForm):
    """
    Form for creating and updating pay heads
    """
    class Meta:
        model = PayHead
        fields = ['name', 'type', 'description', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class EmployeePayHeadForm(forms.ModelForm):
    """
    Form for assigning pay heads to employees
    """
    class Meta:
        model = EmployeePayHead
        fields = ['pay_head', 'amount']


class PayrollForm(forms.ModelForm):
    """
    Form for creating a new payroll run
    """
    class Meta:
        model = Payroll
        fields = ['start_date', 'end_date', 'description', 'notes']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'start_date': 'Start Date',
            'end_date': 'End Date',
            'description': 'Description',
            'notes': 'Notes',
        }
