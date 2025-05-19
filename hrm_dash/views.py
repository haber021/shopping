from django.shortcuts import render
from django.db.models import Count, Sum, Avg
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from core.models import Order, Inventory, Product
from HRM.models import Employee, Department, Attendance, Leave

@login_required
def dashboard(request):
    # HR Stats
    total_employees = Employee.objects.count()
    total_departments = Department.objects.count()
    active_employees = Employee.objects.filter(status='Active').count()

    # Today's Attendance
    today = timezone.now().date()
    attendance_today = Attendance.objects.filter(date=today)
    present_today = attendance_today.filter(status='Present').count()
    absent_today = attendance_today.filter(status='Absent').count()
    late_today = attendance_today.filter(status='Late').count()

    # Leave Stats
    pending_leaves = Leave.objects.filter(status='Pending').count()
    current_on_leave = Leave.objects.filter(
        status='Approved',
        start_date__lte=today,
        end_date__gte=today
    ).count()

    # Retail Stats
    thirty_days_ago = today - timedelta(days=30)
    recent_orders = Order.objects.filter(created_at__gte=thirty_days_ago).order_by('-created_at')
    orders_count = recent_orders.count()
    
    # Set revenue to 0 until a valid total_amount field or computation is defined
    revenue = 0

    # Pending orders
    pending_orders = Order.objects.filter(status='Pending').count()

    # Low stock items
    low_stock_items = Inventory.objects.count()

    context = {
        'total_employees': total_employees,
        'total_departments': total_departments,
        'active_employees': active_employees,
        'present_today': present_today,
        'absent_today': absent_today, 
        'late_today': late_today,
        'pending_leaves': pending_leaves,
        'current_on_leave': current_on_leave,
        'orders_count': orders_count,
        'revenue': revenue,
        'pending_orders': pending_orders,
        'low_stock_items': low_stock_items,
        'products_count': Product.objects.count(),
        'employees_count': total_employees,
    }

    return render(request, 'hrm/dashboard/dashboard.html', context)
