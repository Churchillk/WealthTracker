from django import forms
from .models import *
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

class IncomeSourceForm(forms.ModelForm):
    class Meta:
        model = IncomeSource
        fields = ['name', 'client', 'start_date', 'end_date', 'worth', 'description']
        widgets = {
            'start_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'end_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

class IncomeForm(forms.ModelForm):
    class Meta:
        model = Income
        fields = ['source', 'wallet', 'amount', 'date', 'description']
        widgets = {
            'date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

class ExpensesForm(forms.ModelForm):
    class Meta:
        model = Expenses
        fields = ['name', 'worth', 'description', 'date']
        widgets = {
            'date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

class NowNextForm(forms.ModelForm):
    class Meta:
        model = NowNext
        fields = ['date', 'do', 'done', 'challenges', 'gratitude']
        widgets = {
            'date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'do': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'challenges': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'gratitude': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

class ProjectsForm(forms.ModelForm):
    class Meta:
        model = Projects
        fields = ['name', 'what_next', 'description', 'date_set', 'end_date', 'status']
        widgets = {
            'date_set': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'end_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

class GoalsForm(forms.ModelForm):
    class Meta:
        model = Goals
        fields = ['goal_title', 'goal_description', 'date_set', 'end_date', 'achieved']
        widgets = {
            'date_set': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'end_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'goal_description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'host', 'start_date', 'end_date', 'location', 'category', 'attended']
        widgets = {
            'start_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'end_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'location': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }