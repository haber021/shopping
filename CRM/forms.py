from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import Contact, Lead, Task, Activity

User = get_user_model()

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    remember_me = forms.BooleanField(required=False)

class RegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(max_length=254, required=True)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['first_name', 'last_name', 'email', 'phone', 'company', 'position', 'notes', 'tags']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 4}),
            'tags': forms.TextInput(attrs={'placeholder': 'Comma-separated tags'}),
        }

class LeadForm(forms.ModelForm):
    class Meta:
        model = Lead
        fields = ['title', 'contact', 'value', 'stage', 'priority', 'expected_close_date', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 4}),
            'expected_close_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, user, *args, **kwargs):
        super(LeadForm, self).__init__(*args, **kwargs)
        self.fields['contact'].queryset = Contact.objects.filter(user=user)

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'due_date', 'priority', 'status', 'task_type', 'contact', 'lead']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, user, *args, **kwargs):
        super(TaskForm, self).__init__(*args, **kwargs)
        self.fields['contact'].queryset = Contact.objects.filter(user=user)
        self.fields['lead'].queryset = Lead.objects.filter(user=user)

class ActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = ['activity_type', 'description', 'contact', 'lead', 'task']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, user, *args, **kwargs):
        super(ActivityForm, self).__init__(*args, **kwargs)
        self.fields['contact'].queryset = Contact.objects.filter(user=user)
        self.fields['lead'].queryset = Lead.objects.filter(user=user)
        self.fields['task'].queryset = Task.objects.filter(user=user)

class SettingsForm(forms.ModelForm):
    current_password = forms.CharField(widget=forms.PasswordInput, required=False)
    new_password = forms.CharField(widget=forms.PasswordInput, required=False)
    confirm_password = forms.CharField(widget=forms.PasswordInput, required=False)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')

        if new_password and new_password != confirm_password:
            self.add_error('confirm_password', "Passwords don't match")

        return cleaned_data