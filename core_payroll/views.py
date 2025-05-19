from django.shortcuts import render, redirect
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib import messages
from datetime import datetime, timedelta

from online_payroll.models import Employee, Payroll
from core.models import Product, Order

def demo_login(request):
    from django.contrib.auth.models import User
    
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'adminpassword')
    
    user = authenticate(request, username='admin', password='adminpassword')
    if user is not None:
        login(request, user)
        messages.success(request, "Welcome to RetailPay Philippines! You are logged in as admin.")
        return redirect('core_payroll:dashboard')
    else:
        messages.error(request, "Could not log in with demo credentials. Please try manual login.")
        return redirect('login')

@login_required
def dashboard(request):
    today = datetime.now().date()

    # ✅ Calculate today's sales based on OrderItems
    todays_sales = Order.objects.filter(
        created_at__date=today
    ).annotate(
        order_total=Sum(ExpressionWrapper(F('items__price') * F('items__quantity'), output_field=DecimalField()))
    ).aggregate(
        total_sales=Sum('order_total')
    )['total_sales'] or 0

    low_stock_count = sum(1 for product in Product.objects.all() if product.current_stock <= 10)



    pending_orders = Order.objects.filter(
        status='pending'
    ).count()

    next_payroll_date = today + timedelta(days=(15 - today.day) % 15 or 15)
    employee_count = Employee.objects.filter(active=True).count()

    total_payroll_amount = Employee.objects.filter(
        active=True
    ).aggregate(Sum('base_salary'))['base_salary__sum'] or 0

    recent_orders = Order.objects.order_by('-created_at')[:3]
    recent_payrolls = Payroll.objects.order_by('-processed_at')[:2]
    recent_employees = Employee.objects.order_by('-join_date')[:2]

    recent_activity = []

    for order in recent_orders:
        created_at = order.created_at.replace(tzinfo=None) if order.created_at.tzinfo else order.created_at
        recent_activity.append({
            'type': 'order',
            'message': f"Order #{order.id} {order.status}",
            'date': created_at
        })

    for payroll in recent_payrolls:
        processed_at = payroll.processed_at.replace(tzinfo=None) if payroll.processed_at.tzinfo else payroll.processed_at
        recent_activity.append({
            'type': 'payroll',
            'message': f"Payroll processed for {payroll.start_date.strftime('%b %d')} - {payroll.end_date.strftime('%b %d')}",
            'date': processed_at
        })

    for employee in recent_employees:
        join_datetime = datetime.combine(employee.join_date, datetime.min.time())
        recent_activity.append({
            'type': 'employee',
            'message': f"New employee added ({employee.last_name}, {employee.first_name})",
            'date': join_datetime
        })

    recent_activity = sorted(
        recent_activity, 
        key=lambda x: x['date'],
        reverse=True
    )[:5]

    context = {
        'todays_sales': todays_sales,
        'low_stock_count': low_stock_count,
        'pending_orders': pending_orders,
        'next_payroll_date': next_payroll_date,
        'employee_count': employee_count,
        'total_payroll_amount': total_payroll_amount,
        'recent_activity': recent_activity,
    }

    return render(request, 'payroll/dashboard.html', context)
