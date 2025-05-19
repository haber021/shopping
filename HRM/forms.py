from django import forms
from .models import (
    Employee, Department, Position, Attendance,
    Schedule, Leave, JobApplication, EmployeeDocument
)
from django.utils import timezone


class EmployeeForm(forms.ModelForm):
    """Form for adding/editing employees"""
    hire_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        initial=timezone.now().date
    )
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )

    class Meta:
        model = Employee
        fields = [
            'employee_id', 'first_name', 'last_name', 'email', 
            'phone', 'hire_date', 'department', 'position', 
            'manager', 'status', 'gender', 'date_of_birth', 
            'address', 'emergency_contact_name', 'emergency_contact_phone'
        ]
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make all fields have form-control class for Bootstrap styling
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})
            
        # Filter managers to only active employees
        self.fields['manager'].queryset = Employee.objects.filter(status='Active')
        
        # If it's a new employee, generate next employee_id
        if not self.instance.pk:
            last_employee = Employee.objects.order_by('-employee_id').first()
            if last_employee and last_employee.employee_id.startswith('EMP'):
                try:
                    last_id = int(last_employee.employee_id[3:])
                    next_id = last_id + 1
                    self.fields['employee_id'].initial = f"EMP{next_id:04d}"
                except ValueError:
                    self.fields['employee_id'].initial = "EMP0001"
            else:
                self.fields['employee_id'].initial = "EMP0001"


class DepartmentForm(forms.ModelForm):
    """Form for adding/editing departments"""
    class Meta:
        model = Department
        fields = ['name', 'description', 'manager']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})
        
        # Filter managers to only active employees
        self.fields['manager'].queryset = Employee.objects.filter(status='Active')
        self.fields['description'].widget = forms.Textarea(attrs={'rows': 3, 'class': 'form-control'})


class PositionForm(forms.ModelForm):
    """Form for adding/editing positions"""
    class Meta:
        model = Position
        fields = ['title', 'department', 'description', 'min_salary', 'max_salary']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})
        
        self.fields['description'].widget = forms.Textarea(attrs={'rows': 3, 'class': 'form-control'})


class AttendanceForm(forms.ModelForm):
    """Form for recording attendance"""
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        initial=timezone.now().date
    )
    time_in = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        required=False
    )
    time_out = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        required=False
    )
    
    class Meta:
        model = Attendance
        fields = ['employee', 'date', 'time_in', 'time_out', 'status', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})
        
        # Filter employees to only active employees
        self.fields['employee'].queryset = Employee.objects.filter(status='Active')


class BulkAttendanceForm(forms.Form):
    """Form for recording attendance for multiple employees at once"""
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        initial=timezone.now().date
    )
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )


class ScheduleForm(forms.ModelForm):
    """Form for setting employee schedules"""
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        initial=timezone.now().date
    )
    start_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time'})
    )
    end_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time'})
    )
    
    class Meta:
        model = Schedule
        fields = ['employee', 'date', 'shift_type', 'start_time', 'end_time', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})
        
        # Filter employees to only active employees
        self.fields['employee'].queryset = Employee.objects.filter(status='Active')


class BulkScheduleForm(forms.Form):
    """Form for setting schedules for multiple employees at once"""
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        initial=timezone.now().date
    )
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    shift_type = forms.ChoiceField(
        choices=Schedule.SHIFT_TYPES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    start_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'})
    )
    end_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'})
    )
    notes = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        required=False
    )


class LeaveForm(forms.ModelForm):
    """Form for applying for leave"""
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        initial=timezone.now().date
    )
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        initial=timezone.now().date
    )
    
    class Meta:
        model = Leave
        fields = ['employee', 'leave_type', 'start_date', 'end_date', 'reason']
        widgets = {
            'reason': forms.Textarea(attrs={'rows': 3}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})
        
        # Filter employees to only active employees
        self.fields['employee'].queryset = Employee.objects.filter(status='Active')
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError("End date must be after start date.")
        
        return cleaned_data


class LeaveApprovalForm(forms.ModelForm):
    """Form for approving/rejecting leave requests"""
    class Meta:
        model = Leave
        fields = ['status']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})
        
        # Limit status choices to only Approved/Rejected
        self.fields['status'].choices = [
            ('Approved', 'Approved'),
            ('Rejected', 'Rejected'),
        ]


class JobApplicationForm(forms.ModelForm):
    """Form for recording job applications"""
    application_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        initial=timezone.now().date
    )
    interview_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )
    interview_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time'}),
        required=False
    )
    
    class Meta:
        model = JobApplication
        fields = [
            'position', 'applicant_name', 'email', 'phone',
            'resume_path', 'cover_letter', 'application_date',
            'status', 'notes', 'interview_date', 'interview_time',
            'interview_notes'
        ]
        widgets = {
            'cover_letter': forms.Textarea(attrs={'rows': 3}),
            'notes': forms.Textarea(attrs={'rows': 3}),
            'interview_notes': forms.Textarea(attrs={'rows': 3}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})


class EmployeeDocumentForm(forms.ModelForm):
    """Form for uploading employee documents"""
    expiry_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )
    
    class Meta:
        model = EmployeeDocument
        fields = ['employee', 'document_type', 'title', 'description', 'file_path', 'expiry_date']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})
