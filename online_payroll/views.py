from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Q
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO
from decimal import Decimal
from datetime import date, datetime, timedelta

from .models import (
    Employee, Department, PayHead, EmployeePayHead, 
    Payroll, SalarySlip, SalarySlipDetail
)
from .forms import (
    EmployeeForm, DepartmentForm, PayHeadForm, 
    EmployeePayHeadForm, PayrollForm
)
from .utils import generate_salary_slip_pdf


@login_required
def employee_list(request):
    """
    View for listing all employees with filtering options
    """
    employees = Employee.objects.all()
    
    # Filter by department if provided
    department_id = request.GET.get('department')
    if department_id:
        employees = employees.filter(department_id=department_id)
    
    # Filter by employment type if provided
    employment_type = request.GET.get('type')
    if employment_type:
        employees = employees.filter(employment_type=employment_type)
    
    # Filter by active status
    status = request.GET.get('status', 'active')
    if status == 'active':
        employees = employees.filter(active=True)
    elif status == 'inactive':
        employees = employees.filter(active=False)
    
    # Filter by search term
    search = request.GET.get('search')
    if search:
        employees = employees.filter(
            Q(first_name__icontains=search) | 
            Q(last_name__icontains=search) |
            Q(employee_id__icontains=search)
        )
    
    departments = Department.objects.all()
    employment_types = Employee.TYPE_CHOICES
    
    context = {
        'employees': employees,
        'departments': departments,
        'employment_types': employment_types,
        'selected_department': department_id,
        'selected_type': employment_type,
        'selected_status': status,
        'search_term': search,
    }
    
    return render(request, 'payroll/payroll/employees.html', context)


@login_required
def employee_detail(request, pk):
    """
    View for viewing and managing the details of an employee
    """
    employee = get_object_or_404(Employee, pk=pk)
    
    employee_pay_heads = EmployeePayHead.objects.filter(employee=employee)
    
    # Get all pay heads not assigned to this employee
    assigned_pay_head_ids = employee_pay_heads.values_list('pay_head_id', flat=True)
    available_pay_heads = PayHead.objects.filter(is_active=True).exclude(id__in=assigned_pay_head_ids)
    
    # Handle adding new pay head to employee
    if request.method == 'POST' and 'add_pay_head' in request.POST:
        form = EmployeePayHeadForm(request.POST)
        if form.is_valid():
            employee_pay_head = form.save(commit=False)
            employee_pay_head.employee = employee
            employee_pay_head.created_by = request.user
            employee_pay_head.save()
            messages.success(request, f"Pay head '{employee_pay_head.pay_head.name}' added successfully.")
            return redirect('payroll:employee_detail', pk=employee.pk)
    else:
        form = EmployeePayHeadForm()
    
    # Get recent salary slips
    recent_salary_slips = SalarySlip.objects.filter(employee=employee).order_by('-created_at')[:5]
    
    context = {
        'employee': employee,
        'employee_pay_heads': employee_pay_heads,
        'available_pay_heads': available_pay_heads,
        'form': form,
        'recent_salary_slips': recent_salary_slips,
    }
    
    return render(request, 'payroll/payroll/employee_detail.html', context)


@login_required
def add_employee(request):
    """
    View for adding a new employee
    """
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            employee = form.save(commit=False)
            employee.created_by = request.user
            employee.save()
            messages.success(request, f"Employee '{employee.full_name}' added successfully.")
            return redirect('payroll:employee_list')
    else:
        form = EmployeeForm()
    
    context = {
        'form': form,
        'title': 'Add New Employee',
    }
    
    return render(request, 'payroll/payroll/employee_form.html', context)


@login_required
def edit_employee(request, pk):
    """
    View for editing an existing employee
    """
    employee = get_object_or_404(Employee, pk=pk)
    
    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            employee = form.save(commit=False)
            employee.updated_by = request.user
            employee.save()
            messages.success(request, f"Employee '{employee.full_name}' updated successfully.")
            return redirect('payroll:employee_detail', pk=employee.pk)
    else:
        form = EmployeeForm(instance=employee)
    
    context = {
        'form': form,
        'title': 'Edit Employee',
        'employee': employee,
    }
    
    return render(request, 'payroll/payroll/employee_form.html', context)


@login_required
def pay_heads(request):
    """
    View for managing pay heads
    """
    pay_heads = PayHead.objects.all()
    
    if request.method == 'POST':
        form = PayHeadForm(request.POST)
        if form.is_valid():
            pay_head = form.save(commit=False)
            pay_head.created_by = request.user
            pay_head.save()
            messages.success(request, f"Pay head '{pay_head.name}' added successfully.")
            return redirect('payroll:pay_heads')
    else:
        form = PayHeadForm()
    
    context = {
        'pay_heads': pay_heads,
        'form': form,
    }
    
    return render(request, 'payroll/payroll/pay_heads.html', context)


@login_required
def edit_pay_head(request, pk):
    """
    View for editing an existing pay head
    """
    pay_head = get_object_or_404(PayHead, pk=pk)
    
    if request.method == 'POST':
        form = PayHeadForm(request.POST, instance=pay_head)
        if form.is_valid():
            pay_head = form.save(commit=False)
            pay_head.updated_by = request.user
            pay_head.save()
            messages.success(request, f"Pay head '{pay_head.name}' updated successfully.")
            return redirect('payroll:pay_heads')
    else:
        form = PayHeadForm(instance=pay_head)
    
    context = {
        'form': form,
        'pay_head': pay_head,
    }
    
    return render(request, 'payroll/payroll/edit_pay_head.html', context)


@login_required
def salary_slip(request, pk):
    """
    View for viewing a salary slip
    """
    salary_slip = get_object_or_404(SalarySlip, pk=pk)
    
    # Get earnings and deductions
    earnings = salary_slip.details.filter(type='earning')
    deductions = salary_slip.details.filter(type='deduction')
    
    context = {
        'salary_slip': salary_slip,
        'earnings': earnings,
        'deductions': deductions,
    }
    
    # Generate PDF if requested
    if request.GET.get('format') == 'pdf':
        return generate_salary_slip_pdf(salary_slip)
    
    return render(request, 'payroll/payroll/salary_slip.html', context)


@login_required
def run_payroll(request):
    """
    View for running a new payroll
    """
    if request.method == 'POST':
        form = PayrollForm(request.POST)
        if form.is_valid():
            payroll = form.save(commit=False)
            payroll.created_by = request.user
            payroll.save()
            
            # Process all active employees
            employees = Employee.objects.filter(active=True)
            
            for employee in employees:
                # Calculate basic salary (prorated if needed)
                basic_salary = employee.base_salary
                
                # Get all earnings
                earnings_queryset = EmployeePayHead.objects.filter(
                    employee=employee,
                    pay_head__type='earning'
                )
                
                # Safely aggregate earnings (handle None case)
                earnings_sum = earnings_queryset.aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
                total_earnings = basic_salary + earnings_sum
                
                # Get all deductions
                deductions_queryset = EmployeePayHead.objects.filter(
                    employee=employee,
                    pay_head__type='deduction'
                )
                
                # Safely aggregate deductions (handle None case)
                deductions_sum = deductions_queryset.aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
                total_deductions = deductions_sum
                
                # Calculate net salary
                net_salary = total_earnings - total_deductions
                
                # Create salary slip
                slip = SalarySlip.objects.create(
                    payroll=payroll,
                    employee=employee,
                    basic_salary=basic_salary,
                    total_earnings=total_earnings,
                    total_deductions=total_deductions,
                    net_salary=net_salary,
                    created_by=request.user
                )
                
                # Add basic salary as an earning
                SalarySlipDetail.objects.create(
                    salary_slip=slip,
                    pay_head_name='Basic Salary',
                    type='earning',
                    amount=basic_salary,
                    created_by=request.user
                )
                
                # Add all earnings
                for earning in earnings_queryset:
                    SalarySlipDetail.objects.create(
                        salary_slip=slip,
                        pay_head_name=earning.pay_head.name,
                        type='earning',
                        amount=earning.amount,
                        created_by=request.user
                    )
                
                # Add all deductions
                for deduction in deductions_queryset:
                    SalarySlipDetail.objects.create(
                        salary_slip=slip,
                        pay_head_name=deduction.pay_head.name,
                        type='deduction',
                        amount=deduction.amount,
                        created_by=request.user
                    )
            
            messages.success(request, f"Payroll processed successfully for {employees.count()} employees.")
            return redirect('payroll:payroll_list')
    else:
        # Default to current month
        today = date.today()
        start_date = date(today.year, today.month, 1)
        if today.month == 12:
            end_date = date(today.year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(today.year, today.month + 1, 1) - timedelta(days=1)
        
        form = PayrollForm(initial={
            'start_date': start_date,
            'end_date': end_date,
            'description': f"Monthly Payroll - {start_date.strftime('%B %Y')}"
        })
    
    context = {
        'form': form,
    }
    
    return render(request, 'payroll/payroll/run_payroll.html', context)


@login_required
def payroll_list(request):
    """
    View for listing all payrolls
    """
    payrolls = Payroll.objects.all().order_by('-created_at')
    
    context = {
        'payrolls': payrolls,
    }
    
    return render(request, 'payroll/payroll/payroll_list.html', context)
