from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta
from .models import Lead, Activity, Task, Contact

def get_lead_counts_by_stage(user):
    # Ensure that user is an instance of the User model
    if not user.is_authenticated:
        raise ValueError("The user must be authenticated.")
    
    # Filter Leads based on the authenticated user and aggregate by stage
    lead_counts = Lead.objects.filter(user=user) \
                               .values('stage') \
                               .annotate(count=Count('id')) \
                               .order_by('stage')
    return lead_counts

def get_lead_value_by_stage(user):
    return Lead.objects.filter(user=user).values('stage').annotate(total_value=Sum('value')).order_by('stage')

def get_recent_activities(user, limit=5):
    return Activity.objects.filter(user=user).order_by('-created_at')[:limit]

def get_tasks_due_soon(user, days=7):
    today = timezone.now().date()
    end_date = today + timedelta(days=days)
    return Task.objects.filter(
        user=user,
        due_date__date__range=[today, end_date],
        status='Pending'
    ).order_by('due_date')

def get_total_counts(user):
    return {
        'contacts': Contact.objects.filter(user=user).count(),
        'leads': Lead.objects.filter(user=user).count(),
        'tasks': Task.objects.filter(user=user, status='Pending').count(),
        'activities': Activity.objects.filter(user=user).count(),
    }

def create_activity(user, activity_type, description, contact=None, lead=None, task=None):
    return Activity.objects.create(
        user=user,
        activity_type=activity_type,
        description=description,
        contact=contact,
        lead=lead,
        task=task
    )

def get_monthly_lead_data(user, months=6):
    from django.db.models.functions import TruncMonth
    from django.db.models import Count
    
    end_date = timezone.now()
    start_date = end_date - timedelta(days=30*months)
    
    monthly_data = Lead.objects.filter(
        user=user,
        created_at__range=[start_date, end_date]
    ).annotate(
        month=TruncMonth('created_at')
    ).values('month').annotate(
        count=Count('id'),
        won=Count('id', filter=Q(stage='Closed-Won')),
        lost=Count('id', filter=Q(stage='Closed-Lost'))
    ).order_by('month')
    
    return list(monthly_data)