from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings   
    

class Department(models.Model):
    """Model for company departments"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    manager = models.ForeignKey('Employee', on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_department')
    
    def __str__(self):
        return self.name

class Position(models.Model):
    """Model for job positions"""
    title = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='positions')
    description = models.TextField(blank=True, null=True)
    min_salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    max_salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    def __str__(self):
        return self.title

class Employee(models.Model):
    """Model for employees"""
    GENDER_CHOICES = (
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    )
    
    STATUS_CHOICES = (
        ('Active', 'Active'),
        ('On Leave', 'On Leave'),
        ('Terminated', 'Terminated'),
        ('Retired', 'Retired'),
    )
    
    employee_id = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    hire_date = models.DateField()
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='employees')
    position = models.ForeignKey(Position, on_delete=models.SET_NULL, null=True, blank=True, related_name='employees')
    manager = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subordinates')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True, null=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True, null=True)
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='employee')
# user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.employee_id})"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

class Attendance(models.Model):
    """Model for employee attendance"""
    STATUS_CHOICES = (
        ('Present', 'Present'),
        ('Absent', 'Absent'),
        ('Late', 'Late'),
        ('Half Day', 'Half Day'),
        ('On Leave', 'On Leave'),
    )
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    time_in = models.DateTimeField(null=True, blank=True)
    time_out = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        unique_together = ['employee', 'date']
        
    def __str__(self):
        return f"{self.employee} - {self.date} - {self.status}"

class Schedule(models.Model):
    """Model for employee work schedules"""
    SHIFT_TYPES = (
        ('Morning', 'Morning Shift'),
        ('Afternoon', 'Afternoon Shift'),
        ('Evening', 'Evening Shift'),
        ('Night', 'Night Shift'),
        ('Custom', 'Custom Hours'),
    )
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='schedules')
    date = models.DateField()
    shift_type = models.CharField(max_length=20, choices=SHIFT_TYPES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        unique_together = ['employee', 'date']
        
    def __str__(self):
        return f"{self.employee} - {self.date} - {self.shift_type}"

class Leave(models.Model):
    """Model for employee leave requests"""
    LEAVE_TYPES = (
        ('Annual', 'Annual Leave'),
        ('Sick', 'Sick Leave'),
        ('Maternity', 'Maternity Leave'),
        ('Paternity', 'Paternity Leave'),
        ('Unpaid', 'Unpaid Leave'),
        ('Other', 'Other'),
    )
    
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
        ('Cancelled', 'Cancelled'),
    )
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leave_requests')
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPES)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    approved_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_leaves')
    approved_date = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.employee} - {self.leave_type} ({self.start_date} to {self.end_date})"

class JobApplication(models.Model):
    """Model for job applications"""
    STATUS_CHOICES = (
        ('New', 'New'),
        ('Screening', 'Screening'),
        ('Interview', 'Interview'),
        ('Assessment', 'Assessment'),
        ('Offer', 'Offer'),
        ('Hired', 'Hired'),
        ('Rejected', 'Rejected'),
    )
    
    position = models.ForeignKey(Position, on_delete=models.CASCADE, related_name='applications')
    applicant_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    application_date = models.DateField(default=timezone.now)
    resume_path = models.CharField(max_length=255, blank=True, null=True)
    cover_letter = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='New')
    notes = models.TextField(blank=True, null=True)
    interview_date = models.DateField(null=True, blank=True)
    interview_time = models.TimeField(null=True, blank=True)
    interview_notes = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.applicant_name} - {self.position} ({self.status})"

class EmployeeDocument(models.Model):
    """Model for employee documents"""
    DOCUMENT_TYPES = (
        ('ID', 'ID/Passport'),
        ('Resume', 'Resume/CV'),
        ('Contract', 'Employment Contract'),
        ('Certificate', 'Certificates'),
        ('Performance', 'Performance Review'),
        ('Other', 'Other'),
    )
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    file_path = models.CharField(max_length=255)
    upload_date = models.DateField(auto_now_add=True)
    expiry_date = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.employee} - {self.title} ({self.document_type})"