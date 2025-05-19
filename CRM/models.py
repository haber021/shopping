from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.contrib.auth.models import User
from django.db import models
from django.conf import settings
from core.models import User




from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

class User(AbstractUser):
    role = models.CharField(max_length=20, default='user')
    
    # Add these to resolve the reverse accessor clash
    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_name="crm_user_groups",  # Changed
        related_query_name="crm_user",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="crm_user_permissions",  # Changed
        related_query_name="crm_user",
    )
    
    def __str__(self):
        return self.username
    

from django.db import models
from django.conf import settings
from django.utils import timezone

class Contact(models.Model):
    PRIORITY_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    company = models.CharField(max_length=100, blank=True, null=True)
    position = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    tags = models.CharField(max_length=200, blank=True, null=True)
    last_contacted = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['first_name', 'last_name']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Lead(models.Model):
    STAGE_CHOICES = [
        ('New', 'New'),
        ('Contacted', 'Contacted'),
        ('Proposal', 'Proposal'),
        ('Closed-Won', 'Closed-Won'),
        ('Closed-Lost', 'Closed-Lost'),
    ]
    
    PRIORITY_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    stage = models.CharField(max_length=20, choices=STAGE_CHOICES, default='New')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='Medium')
    notes = models.TextField(blank=True, null=True)
    expected_close_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title

class Task(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]
    
    PRIORITY_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
    ]
    
    TYPE_CHOICES = [
        ('Call', 'Call'),
        ('Email', 'Email'),
        ('Meeting', 'Meeting'),
        ('Follow-up', 'Follow-up'),
        ('Other', 'Other'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    contact = models.ForeignKey(Contact, on_delete=models.SET_NULL, blank=True, null=True)
    lead = models.ForeignKey(Lead, on_delete=models.SET_NULL, blank=True, null=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    due_date = models.DateTimeField()
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='Medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    task_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='Other')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['due_date']
    
    def __str__(self):
        return self.title

class Activity(models.Model):
    TYPE_CHOICES = [
        ('Call', 'Call'),
        ('Email', 'Email'),
        ('Meeting', 'Meeting'),
        ('Note', 'Note'),
        ('Other', 'Other'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    contact = models.ForeignKey(Contact, on_delete=models.SET_NULL, blank=True, null=True)
    lead = models.ForeignKey(Lead, on_delete=models.SET_NULL, blank=True, null=True)
    task = models.ForeignKey(Task, on_delete=models.SET_NULL, blank=True, null=True)
    activity_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    description = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Activities'
    
    def __str__(self):
        return f"{self.activity_type} - {self.description[:50]}"