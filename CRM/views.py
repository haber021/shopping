import json
from datetime import datetime, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from django.urls import reverse
from core.models import User
from .models import  Contact, Lead, Task, Activity
from .forms import (LoginForm, RegistrationForm, ContactForm, LeadForm, TaskForm, 
                   ActivityForm, SettingsForm)
from .utils import (get_lead_counts_by_stage, get_recent_activities, get_tasks_due_soon, 
                   get_total_counts, create_activity, get_monthly_lead_data, get_lead_value_by_stage)

def index(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'crm/index.html')

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password']
            )
            if user is not None:
                auth_login(request, user)
                if form.cleaned_data['remember_me']:
                    request.session.set_expiry(1209600)  # 2 weeks
                next_page = request.GET.get('next', 'dashboard')
                return redirect(next_page)
            else:
                messages.error(request, 'Invalid username or password')
        else:
            messages.error(request, 'Please correct the errors below')
    else:
        form = LoginForm()
    
    return render(request, 'crm/login.html', {'form': form})

def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Registration successful! Please login.')
            return redirect('login')
        else:
            messages.error(request, 'Please correct the errors below')
    else:
        form = RegistrationForm()
    
    return render(request, 'crm/register.html', {'form': form})

def logout_view(request):
    auth_logout(request)
    return redirect('crm/index')

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import json
from .utils import get_lead_counts_by_stage, get_lead_value_by_stage, get_recent_activities, get_tasks_due_soon, get_total_counts, get_monthly_lead_data

@login_required
def dashboard(request):
    try:
        # Fetch data for the dashboard
        lead_counts = get_lead_counts_by_stage(request.user)
        lead_values = get_lead_value_by_stage(request.user)
        recent_activities = get_recent_activities(request.user)
        upcoming_tasks = get_tasks_due_soon(request.user)
        counts = get_total_counts(request.user)
        monthly_data = get_monthly_lead_data(request.user)
        
        # Render the dashboard template with the fetched data
        return render(request, 'crm/dashboard.html', {
            'lead_counts': lead_counts,
            'lead_values': lead_values,
            'recent_activities': recent_activities,
            'upcoming_tasks': upcoming_tasks,
            'counts': counts,
            'monthly_data': json.dumps(monthly_data)  # Convert monthly data to JSON for rendering in JavaScript
        })
    
    except Exception as e:
        # Handle any errors that occur and show an error message in the dashboard
        print(f"Error in dashboard view: {e}")
        return render(request, 'crm/dashboard.html', {
            'error_message': 'An error occurred while fetching the dashboard data. Please try again later.'
        })



from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Contact

@login_required
def contacts(request):
    # Get the contacts related to the logged-in user
    contacts = Contact.objects.filter(user=request.user)

    # Ensure we have a proper User instance
    if not hasattr(request.user, 'id'):
        return redirect('login')
    
    search = request.GET.get('search', '')
    sort = request.GET.get('sort', 'name')
    
    # Apply search filter if there's a search term
    if search:
        contacts = contacts.filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(email__icontains=search) |
            Q(company__icontains=search) |
            Q(tags__icontains=search)
        )
    
    # Apply sorting based on the 'sort' parameter
    if sort == 'name':
        contacts = contacts.order_by('first_name', 'last_name')
    elif sort == 'company':
        contacts = contacts.order_by('company')
    elif sort == 'recent':
        contacts = contacts.order_by('-last_contacted')
    
    return render(request, 'crm/contacts.html', {
        'contacts': contacts,
        'search': search,
        'sort': sort
    })


@login_required
def new_contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save(commit=False)
            contact.user = request.user
            contact.save()
            
            create_activity(
                user=request.user,
                activity_type='Note',
                description=f'Created new contact: {contact.first_name} {contact.last_name}',
                contact=contact
            )
            
            messages.success(request, 'Contact created successfully!')
            return redirect('contacts')
    else:
        form = ContactForm()
    
    return render(request, 'crm/contact_detail.html', {'form': form, 'title': 'New Contact'})

@login_required
def edit_contact(request, contact_id):
    contact = get_object_or_404(Contact, id=contact_id, user=request.user)
    
    if request.method == 'POST':
        form = ContactForm(request.POST, instance=contact)
        if form.is_valid():
            form.save()
            
            create_activity(
                user=request.user,
                activity_type='Note',
                description=f'Updated contact: {contact.first_name} {contact.last_name}',
                contact=contact
            )
            
            messages.success(request, 'Contact updated successfully!')
            return redirect('contacts')
    else:
        form = ContactForm(instance=contact)
    
    related_leads = Lead.objects.filter(contact=contact)
    related_tasks = Task.objects.filter(contact=contact)
    related_activities = Activity.objects.filter(contact=contact).order_by('-created_at')
    
    return render(request, 'crm/contact_detail.html', {
        'form': form,
        'contact': contact,
        'leads': related_leads,
        'tasks': related_tasks,
        'activities': related_activities,
        'title': 'Edit Contact'
    })

@login_required
def delete_contact(request, contact_id):
    contact = get_object_or_404(Contact, id=contact_id, user=request.user)
    
    if Lead.objects.filter(contact=contact).exists() or Task.objects.filter(contact=contact).exists():
        messages.error(request, 'Cannot delete contact with related leads or tasks.')
        return redirect('edit_contact', contact_id=contact.id)
    
    Activity.objects.filter(contact=contact).delete()
    contact.delete()
    
    messages.success(request, 'Contact deleted successfully!')
    return redirect('contacts')

@login_required
def leads(request):
    stage_filter = request.GET.get('stage', '')
    search = request.GET.get('search', '')
    
    leads = Lead.objects.filter(user=request.user)
    
    if stage_filter:
        leads = leads.filter(stage=stage_filter)
    
    if search:
        leads = leads.filter(
            Q(contact__first_name__icontains=search) |
            Q(contact__last_name__icontains=search) |
            Q(contact__company__icontains=search) |
            Q(title__icontains=search)
        )
    
    stages = ['New', 'Contacted', 'Proposal', 'Closed-Won', 'Closed-Lost']
    leads_by_stage = {stage: leads.filter(stage=stage) for stage in stages}
    
    contacts = Contact.objects.filter(user=request.user)
    form = LeadForm(request.user)
    
    return render(request, 'crm/leads.html', {
        'leads_by_stage': leads_by_stage,
        'stages': stages,
        'form': form,
        'contacts': contacts,
        'stage_filter': stage_filter,
        'search': search
    })

@login_required
def new_lead(request):
    if request.method == 'POST':
        form = LeadForm(request.user, request.POST)
        if form.is_valid():
            lead = form.save(commit=False)
            lead.user = request.user
            lead.save()
            
            contact = lead.contact
            create_activity(
                user=request.user,
                activity_type='Note',
                description=f'Created new lead "{lead.title}" for {contact.first_name} {contact.last_name}',
                contact=contact,
                lead=lead
            )
            
            messages.success(request, 'Lead created successfully!')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    
    return redirect('leads')

@login_required
def edit_lead(request, lead_id):
    lead = get_object_or_404(Lead, id=lead_id, user=request.user)
    
    if request.method == 'POST':
        form = LeadForm(request.user, request.POST, instance=lead)
        if form.is_valid():
            old_stage = lead.stage
            lead = form.save()
            
            if old_stage != lead.stage:
                create_activity(
                    user=request.user,
                    activity_type='Note',
                    description=f'Changed lead "{lead.title}" stage from {old_stage} to {lead.stage}',
                    contact=lead.contact,
                    lead=lead
                )
            else:
                create_activity(
                    user=request.user,
                    activity_type='Note',
                    description=f'Updated lead "{lead.title}"',
                    contact=lead.contact,
                    lead=lead
                )
            
            messages.success(request, 'Lead updated successfully!')
            return redirect('leads')
    else:
        form = LeadForm(request.user, instance=lead)
    
    related_tasks = Task.objects.filter(lead=lead)
    related_activities = Activity.objects.filter(lead=lead).order_by('-created_at')
    
    return render(request, 'crm/lead_detail.html', {
        'form': form,
        'lead': lead,
        'tasks': related_tasks,
        'activities': related_activities
    })

@login_required
def delete_lead(request, lead_id):
    lead = get_object_or_404(Lead, id=lead_id, user=request.user)
    
    if Task.objects.filter(lead=lead).exists():
        messages.error(request, 'Cannot delete lead with related tasks.')
        return redirect('leads')
    
    Activity.objects.filter(lead=lead).delete()
    lead.delete()
    
    messages.success(request, 'Lead deleted successfully!')
    return redirect('leads')

@login_required
def update_lead_stage(request, lead_id):
    if request.method == 'POST':
        lead = get_object_or_404(Lead, id=lead_id, user=request.user)
        new_stage = request.POST.get('stage')
        
        if new_stage not in ['New', 'Contacted', 'Proposal', 'Closed-Won', 'Closed-Lost']:
            return JsonResponse({'success': False, 'message': 'Invalid stage'})
        
        old_stage = lead.stage
        lead.stage = new_stage
        lead.save()
        
        create_activity(
            user=request.user,
            activity_type='Note',
            description=f'Changed lead "{lead.title}" stage from {old_stage} to {new_stage}',
            contact=lead.contact,
            lead=lead
        )
        
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})

@login_required
def tasks(request):
    status_filter = request.GET.get('status', '')
    view = request.GET.get('view', 'list')
    
    tasks = Task.objects.filter(user=request.user)
    
    if status_filter:
        tasks = tasks.filter(status=status_filter)
    else:
        tasks = tasks.filter(status='Pending')
    
    tasks = tasks.order_by('due_date')
    
    contacts = Contact.objects.filter(user=request.user)
    leads = Lead.objects.filter(user=request.user)
    form = TaskForm(request.user)
    
    return render(request, 'crm/tasks.html', {
        'tasks': tasks,
        'view': view,
        'form': form,
        'contacts': contacts,
        'leads': leads,
        'status_filter': status_filter
    })

@login_required
def new_task(request):
    if request.method == 'POST':
        form = TaskForm(request.user, request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            
            if form.cleaned_data['contact'] == 0:
                task.contact = None
            if form.cleaned_data['lead'] == 0:
                task.lead = None
            
            task.save()
            
            description = f'Created new task: {task.title}'
            if task.contact:
                description += f' for contact {task.contact.full_name}'
            if task.lead:
                description += f' related to lead "{task.lead.title}"'
            
            create_activity(
                user=request.user,
                activity_type='Note',
                description=description,
                contact=task.contact,
                lead=task.lead,
                task=task
            )
            
            messages.success(request, 'Task created successfully!')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    
    return redirect('tasks')

@login_required
def edit_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    
    if request.method == 'POST':
        form = TaskForm(request.user, request.POST, instance=task)
        if form.is_valid():
            status_changed = task.status != form.cleaned_data['status']
            task = form.save(commit=False)
            
            if form.cleaned_data['contact'] == 0:
                task.contact = None
            if form.cleaned_data['lead'] == 0:
                task.lead = None
            
            task.save()
            
            if status_changed:
                create_activity(
                    user=request.user,
                    activity_type='Note',
                    description=f'Marked task "{task.title}" as {task.status}',
                    contact=task.contact,
                    lead=task.lead,
                    task=task
                )
            else:
                create_activity(
                    user=request.user,
                    activity_type='Note',
                    description=f'Updated task "{task.title}"',
                    contact=task.contact,
                    lead=task.lead,
                    task=task
                )
            
            messages.success(request, 'Task updated successfully!')
            return redirect('tasks')
    else:
        form = TaskForm(request.user, instance=task)
    
    return render(request, 'crm/task_detail.html', {'form': form, 'task': task})

@login_required
def toggle_task_status(request, task_id):
    if request.method == 'POST':
        task = get_object_or_404(Task, id=task_id, user=request.user)
        task.status = 'Completed' if task.status == 'Pending' else 'Pending'
        task.save()
        
        create_activity(
            user=request.user,
            activity_type='Note',
            description=f'Marked task "{task.title}" as {task.status}',
            contact=task.contact,
            lead=task.lead,
            task=task
        )
        
        return JsonResponse({'success': True, 'status': task.status})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})

@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    Activity.objects.filter(task=task).delete()
    task.delete()
    
    messages.success(request, 'Task deleted successfully!')
    return redirect('tasks')

@login_required
def reports(request):
    months = int(request.GET.get('months', 6))
    monthly_data = get_monthly_lead_data(request.user, months)
    lead_counts = get_lead_counts_by_stage(request.user)
    lead_values = get_lead_value_by_stage(request.user)
    stats = get_total_counts(request.user)
    
    return render(request, 'crm/reports.html', {
        'monthly_data': json.dumps(monthly_data),
        'lead_counts': lead_counts,
        'lead_values': lead_values,
        'stats': stats,
        'months': months
    })

@login_required
def settings(request):
    if request.method == 'POST':
        form = SettingsForm(request.POST, instance=request.user)
        if form.is_valid():
            if form.cleaned_data['current_password'] and form.cleaned_data['new_password']:
                if not request.user.check_password(form.cleaned_data['current_password']):
                    messages.error(request, 'Current password is incorrect.')
                    return redirect('settings')
                
                request.user.set_password(form.cleaned_data['new_password'])
            
            form.save()
            messages.success(request, 'Settings updated successfully!')
            return redirect('settings')
    else:
        form = SettingsForm(instance=request.user)
    
    return render(request, 'crm/settings.html', {'form': form})

@login_required
def log_activity(request):
    if request.method == 'POST':
        form = ActivityForm(request.user, request.POST)
        if form.is_valid():
            activity = form.save(commit=False)
            activity.user = request.user
            
            if form.cleaned_data['contact'] == 0:
                activity.contact = None
            if form.cleaned_data['lead'] == 0:
                activity.lead = None
            if form.cleaned_data['task'] == 0:
                activity.task = None
            
            activity.save()
            
            if activity.contact:
                activity.contact.last_contacted = timezone.now()
                activity.contact.save()
            
            messages.success(request, 'Activity logged successfully!')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    
    return redirect(request.META.get('HTTP_REFERER', 'dashboard'))

@login_required
def api_contacts(request):
    contacts = Contact.objects.filter(user=request.user)
    data = [{
        'id': c.id,
        'name': f"{c.first_name} {c.last_name}",
        'company': c.company or '',
        'email': c.email,
        'phone': c.phone or ''
    } for c in contacts]
    return JsonResponse(data, safe=False)

@login_required
def api_leads(request):
    leads = Lead.objects.filter(user=request.user)
    data = [{
        'id': l.id,
        'title': l.title,
        'stage': l.stage,
        'value': float(l.value),
        'contact': f"{l.contact.first_name} {l.contact.last_name}" if l.contact else "N/A"
    } for l in leads]
    return JsonResponse(data, safe=False)

@login_required
def api_calendar_tasks(request):
    start_date = request.GET.get('start', '')
    end_date = request.GET.get('end', '')
    
    tasks = Task.objects.filter(user=request.user)
    
    if start_date and end_date:
        tasks = tasks.filter(due_date__range=[start_date, end_date])
    
    events = []
    for task in tasks:
        if task.due_date:
            color = '#dc3545' if task.priority == 'High' else '#ffc107' if task.priority == 'Medium' else '#0d6efd'
            if task.status == 'Completed':
                color = '#198754'
                
            events.append({
                'id': task.id,
                'title': task.title,
                'start': task.due_date.strftime('%Y-%m-%d'),
                'description': task.description or '',
                'color': color,
                'extendedProps': {
                    'status': task.status,
                    'priority': task.priority,
                    'type': task.task_type,
                    'contact': task.contact.full_name if task.contact else None,
                    'lead': task.lead.title if task.lead else None
                }
            })
    
    return JsonResponse(events, safe=False)

