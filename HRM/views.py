from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages
from django.db.models import Count

from .models import (
    Department, Position, Employee, Attendance, 
    Schedule, Leave, JobApplication, EmployeeDocument
)

@login_required
def employee_list(request):
    """View for employee list"""
    # For now we'll create a simple stub 
    employees = Employee.objects.all()
    departments = Department.objects.all()
    
    context = {
        'employees': employees,
        'departments': departments,
    }
    return render(request, 'hrm/hr/employees.html', context)

@login_required
def employee_detail(request, employee_id):
    """View for employee details"""
    # Simple stub
    employee = get_object_or_404(Employee, id=employee_id)
    context = {
        'employee': employee,
    }
    return render(request, 'hrm/hr/employee_detail.html', context)

from .forms import EmployeeForm

@login_required
def employee_add(request):
    form = EmployeeForm()
    print("Form fields:", form.fields.keys())  # Debug output
    return render(request, 'hr/employee_form.html', {'form': form})

@login_required
def employee_edit(request, employee_id):
    """View for editing employees"""
    # Simple stub
    employee = get_object_or_404(Employee, id=employee_id)
    return render(request, 'hr/employee_form.html', {'employee': employee})

@login_required
def employee_delete(request, employee_id):
    """View for deleting employees"""
    # Simple stub
    employee = get_object_or_404(Employee, id=employee_id)
    return render(request, 'hr/employee_confirm_delete.html', {'employee': employee})

@login_required
def department_list(request):
    """View for department list"""
    departments = Department.objects.all().order_by('name')
    employees = Employee.objects.filter(status='Active')
    
    context = {
        'departments': departments,
        'employees': employees,
    }
    return render(request, 'hr/departments.html', context)

@login_required
def position_list(request):
    """View for position list"""
    # Simple stub
    return render(request, 'hr/positions.html')

@login_required
def attendance(request):
    """View for attendance management"""
    # Simple stub
    return render(request, 'hr/attendance.html')

@login_required
def attendance_add(request):
    """View for adding attendance records"""
    # Process form if POST, otherwise redirect to attendance page
    if request.method == 'POST':
        # Process form data (stub for now)
        messages.success(request, "Attendance record saved successfully.")
        return redirect('hr:attendance')
    return redirect('hr:attendance')

@login_required
def attendance_bulk(request):
    """View for bulk attendance recording"""
    # Simple stub
    return redirect('hr:attendance')

@login_required
def schedule(request):
    """View for schedule management"""
    # Simple stub
    return render(request, 'hr/schedule.html')

@login_required
def schedule_add(request):
    """View for adding schedules"""
    # Process form if POST, otherwise redirect to schedule page
    if request.method == 'POST':
        # Process form data (stub for now)
        messages.success(request, "Schedule saved successfully.")
        return redirect('hr:schedule')
    return redirect('hr:schedule')

@login_required
def schedule_bulk(request):
    """View for bulk schedule assignment"""
    # Simple stub
    return redirect('hr:schedule')

@login_required
def leave(request):
    """View for leave management"""
    # Simple stub
    return render(request, 'hr/leave.html')

@login_required
def leave_add(request):
    """View for adding leave requests"""
    # Process form if POST, otherwise redirect to leave page
    if request.method == 'POST':
        # Process form data (stub for now)
        messages.success(request, "Leave request submitted successfully.")
        return redirect('hr:leave')
    return redirect('hr:leave')

@login_required
def leave_approve(request, leave_id):
    """View for approving/rejecting leave requests"""
    # Simple stub
    return render(request, 'hr/leave_approve.html')

@login_required
def recruitment(request):
    """View for recruitment management"""
    applications = JobApplication.objects.all().order_by('-application_date')
    positions = Position.objects.all()
    
    # Get recruitment statistics
    recruitment_stats = {
        'total': applications.count(),
        'new': applications.filter(status='New').count(),
        'interviews': applications.filter(status='Interview').count(),
        'offers': applications.filter(status='Offer').count(),
        'hired': applications.filter(status='Hired').count()
    }
    
    # Get status counts for the chart
    status_counts = {
        status: applications.filter(status=status).count()
        for status in ['New', 'Screening', 'Interview', 'Assessment', 'Offer', 'Hired', 'Rejected']
    }
    
    # Get upcoming interviews
    upcoming_interviews = applications.filter(
        status='Interview',
        interview_date__gte=timezone.now()
    ).order_by('interview_date')[:5]
    
    context = {
        'applications': applications,
        'positions': positions,
        'recruitment_stats': recruitment_stats,
        'status_counts': status_counts,
        'upcoming_interviews': upcoming_interviews,
        'status_choices': JobApplication.STATUS_CHOICES,
    }
    return render(request, 'hr/recruitment.html', context)

@login_required
def recruitment_add(request):
    """View for adding job applications"""
    # Process form if POST, otherwise redirect to recruitment page
    if request.method == 'POST':
        # Process form data (stub for now)
        messages.success(request, "Job application added successfully.")
        return redirect('hr:recruitment')
    return redirect('hr:recruitment')

@login_required
def recruitment_detail(request, application_id):
    """View for recruitment detail"""
    # Simple stub
    return render(request, 'hr/recruitment_detail.html')

@login_required
def documents(request):
    """View for document management"""
    # Simple stub
    return render(request, 'hr/documents.html')

@login_required
def document_add(request):
    """View for adding documents"""
    # Process form if POST, otherwise redirect to documents page
    if request.method == 'POST':
        # Process form data (stub for now)
        messages.success(request, "Document uploaded successfully.")
        return redirect('hr:documents')
    return redirect('hr:documents')

@login_required
def document_delete(request, document_id):
    """View for deleting documents"""
    # Simple stub
    return redirect('hr:documents')