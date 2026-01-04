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
        fields = ['name', 'client', 'start_date', 'end_date', 'worth', 'got', 'description']
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
        fields = ['name', 'worth', 'description', 'date', 'category']
        widgets = {
            'date': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control bg-slate-800 border border-slate-700 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-rose-500 focus:border-transparent'
            }),
            'description': forms.Textarea(attrs={
                'rows': 4,
                'class': 'form-control bg-slate-800 border border-slate-700 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-rose-500 focus:border-transparent',
                'placeholder': 'Add any notes about this expense...'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control bg-slate-800 border border-slate-700 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-rose-500 focus:border-transparent',
                'placeholder': 'e.g., Groceries, Rent, Utilities'
            }),
            'worth': forms.NumberInput(attrs={
                'class': 'form-control bg-slate-800 border border-slate-700 rounded-lg px-10 py-3 focus:outline-none focus:ring-2 focus:ring-rose-500 focus:border-transparent',
                'step': '0.01',
                'min': '0'
            }),
            'category': forms.Select(attrs={
                'class': 'hidden',  # We'll use custom buttons instead
                'id': 'categorySelect'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Add currency symbol to worth field
        self.fields['worth'].widget.attrs.update({
            'placeholder': '0.00'
        })

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

class DreamCarForm(forms.ModelForm):
    class Meta:
        model = DreamCar
        fields = ['brand', 'model', 'horsepower', 'year', 'price', 'description']
        widgets = {
            'brand': forms.TextInput(attrs={
                'class': 'bg-slate-800 border border-slate-700 rounded-lg px-4 py-3 w-full focus:outline-none focus:ring-2 focus:ring-emerald-500'
            }),
            'model': forms.TextInput(attrs={
                'class': 'bg-slate-800 border border-slate-700 rounded-lg px-4 py-3 w-full focus:outline-none focus:ring-2 focus:ring-emerald-500'
            }),
            'horsepower': forms.NumberInput(attrs={
                'class': 'bg-slate-800 border border-slate-700 rounded-lg px-4 py-3 w-full focus:outline-none focus:ring-2 focus:ring-emerald-500'
            }),
            'year': forms.NumberInput(attrs={
                'class': 'bg-slate-800 border border-slate-700 rounded-lg px-4 py-3 w-full focus:outline-none focus:ring-2 focus:ring-emerald-500'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'bg-slate-800 border border-slate-700 rounded-lg px-4 py-3 w-full focus:outline-none focus:ring-2 focus:ring-emerald-500',
                'step': '0.01'
            }),
            'description': forms.Textarea(attrs={
                'class': 'bg-slate-800 border border-slate-700 rounded-lg px-4 py-3 w-full focus:outline-none focus:ring-2 focus:ring-emerald-500',
                'rows': 4
            }),
        }
        labels = {
            'horsepower': 'Horsepower (HP)',
            'price': 'Price ($)',
        }

class PictureForm(forms.ModelForm):
    class Meta:
        model = Pictures
        fields = ['brand', 'model', 'year', 'picture']
        widgets = {
            'brand': forms.TextInput(attrs={
                'class': 'bg-slate-800 border border-slate-700 rounded-lg px-4 py-3 w-full focus:outline-none focus:ring-2 focus:ring-emerald-500'
            }),
            'model': forms.TextInput(attrs={
                'class': 'bg-slate-800 border border-slate-700 rounded-lg px-4 py-3 w-full focus:outline-none focus:ring-2 focus:ring-emerald-500'
            }),
            'year': forms.NumberInput(attrs={
                'class': 'bg-slate-800 border border-slate-700 rounded-lg px-4 py-3 w-full focus:outline-none focus:ring-2 focus:ring-emerald-500'
            }),
            'picture': forms.FileInput(attrs={
                'class': 'bg-slate-800 border border-slate-700 rounded-lg px-4 py-3 w-full focus:outline-none focus:ring-2 focus:ring-emerald-500'
            }),
        }