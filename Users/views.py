from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, TemplateView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.urls import reverse_lazy
from django.db.models import Sum, Count
from django.utils import timezone
from django.contrib import messages
from django.http import HttpResponseRedirect
from datetime import timedelta
from Tracker.models import *
from .models import *
from Tracker.forms import *
from .forms import *
import json

# Custom Login View
class CustomLoginView(LoginView):
    form_class = CustomAuthenticationForm
    template_name = 'Users/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('dashboard')

    def form_invalid(self, form):
        messages.error(self.request, 'Invalid username or password. Please try again.')
        return super().form_invalid(form)

# Register View
class RegisterView(FormView):
    template_name = 'Users/register.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        user = form.save()
        # Create UserProfile for the new user
        UserProfile.objects.create(user=user)
        # Log the user in
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password1')
        user = authenticate(username=username, password=password)
        login(self.request, user)
        messages.success(self.request, f'Welcome {username}! Your account has been created successfully.')
        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)

# Custom Logout View
class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('login')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.info(request, 'You have been logged out successfully.')
        return super().dispatch(request, *args, **kwargs)

# Profile View
class ProfileView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    form_class = UserProfileForm
    template_name = 'Users/profile.html'
    success_url = reverse_lazy('profile')

    def get_object(self):
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_form'] = UserUpdateForm(instance=self.request.user)
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Your profile has been updated successfully!')
        return super().form_valid(form)

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

# Dashboard View (remains the same)
class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'tracker/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Calculate totals
        total_income = Income.objects.filter(user=user).aggregate(Sum('amount'))['amount__sum'] or 0
        total_expenses = Expenses.objects.filter(user=user).aggregate(Sum('worth'))['worth__sum'] or 0
        total_worth = IncomeSource.objects.filter(user=user).aggregate(Sum('worth'))['worth__sum'] or 0
        active_projects = Projects.objects.filter(user=user, status='In Progress').count()
        upcoming_events = Event.objects.filter(user=user, start_date__gte=timezone.now()).count()

        # Quick stats data
        context['quick_stats'] = {
            'total_income': total_income,
            'total_expenses': total_expenses,
            'net_worth': total_worth,
            'active_projects': active_projects,
            'upcoming_events': upcoming_events,
            'balance': total_income - total_expenses,
        }

        # Chart data - Last 30 days income
        thirty_days_ago = timezone.now() - timedelta(days=30)
        daily_income = Income.objects.filter(
            user=user,
            date__gte=thirty_days_ago
        ).extra({'day': "date(date)"}).values('day').annotate(total=Sum('amount')).order_by('day')

        income_labels = [item['day'].strftime('%Y-%m-%d') for item in daily_income]
        income_data = [item['total'] for item in daily_income]

        # Expenses by category
        expenses_by_category = {
            'Business': Expenses.objects.filter(user=user, name__icontains='business').aggregate(Sum('worth'))['worth__sum'] or 0,
            'Personal': Expenses.objects.filter(user=user, name__icontains='personal').aggregate(Sum('worth'))['worth__sum'] or 0,
            'Investment': Expenses.objects.filter(user=user, name__icontains='investment').aggregate(Sum('worth'))['worth__sum'] or 0,
        }

        context['chart_data'] = {
            'income_labels': json.dumps(income_labels),
            'income_data': json.dumps(income_data),
            'expense_labels': json.dumps(list(expenses_by_category.keys())),
            'expense_data': json.dumps(list(expenses_by_category.values())),
        }

        # Recent activities
        context['recent_incomes'] = Income.objects.filter(user=user).order_by('-date')[:5]
        context['recent_expenses'] = Expenses.objects.filter(user=user).order_by('-date')[:5]
        context['upcoming_events_list'] = Event.objects.filter(
            user=user,
            start_date__gte=timezone.now()
        ).order_by('start_date')[:5]

        return context

# The rest of your CRUD views remain the same...
# IncomeSource Views
class IncomeSourceListView(LoginRequiredMixin, ListView):
    model = IncomeSource
    template_name = 'tracker/incomesource_list.html'
    context_object_name = 'incomesources'

    def get_queryset(self):
        return IncomeSource.objects.filter(user=self.request.user)

class IncomeSourceCreateView(LoginRequiredMixin, CreateView):
    model = IncomeSource
    form_class = IncomeSourceForm
    template_name = 'tracker/incomesource_form.html'
    success_url = reverse_lazy('incomesource-list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Income source created successfully!')
        return super().form_valid(form)

class IncomeSourceUpdateView(LoginRequiredMixin, UpdateView):
    model = IncomeSource
    form_class = IncomeSourceForm
    template_name = 'tracker/incomesource_form.html'
    success_url = reverse_lazy('incomesource-list')

    def get_queryset(self):
        return IncomeSource.objects.filter(user=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, 'Income source updated successfully!')
        return super().form_valid(form)

class IncomeSourceDeleteView(LoginRequiredMixin, DeleteView):
    model = IncomeSource
    template_name = 'tracker/incomesource_confirm_delete.html'
    success_url = reverse_lazy('incomesource-list')

    def get_queryset(self):
        return IncomeSource.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Income source deleted successfully!')
        return super().delete(request, *args, **kwargs)

# Income Views
class IncomeListView(LoginRequiredMixin, ListView):
    model = Income
    template_name = 'tracker/income_list.html'
    context_object_name = 'incomes'
    paginate_by = 10

    def get_queryset(self):
        return Income.objects.filter(user=self.request.user).order_by('-date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['total_income'] = Income.objects.filter(user=user).aggregate(Sum('amount'))['amount__sum'] or 0

        # This month's income
        start_of_month = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        context['month_income'] = Income.objects.filter(
            user=user,
            date__gte=start_of_month
        ).aggregate(Sum('amount'))['amount__sum'] or 0

        # Average monthly income
        total_months = max(1, Income.objects.filter(user=user).dates('date', 'month').distinct().count())
        context['avg_income'] = context['total_income'] / total_months

        return context

class IncomeCreateView(LoginRequiredMixin, CreateView):
    model = Income
    form_class = IncomeForm
    template_name = 'tracker/income_form.html'
    success_url = reverse_lazy('income-list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Income record added successfully!')
        return super().form_valid(form)

class IncomeUpdateView(LoginRequiredMixin, UpdateView):
    model = Income
    form_class = IncomeForm
    template_name = 'tracker/income_form.html'
    success_url = reverse_lazy('income-list')

    def get_queryset(self):
        return Income.objects.filter(user=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, 'Income record updated successfully!')
        return super().form_valid(form)

class IncomeDeleteView(LoginRequiredMixin, DeleteView):
    model = Income
    template_name = 'tracker/income_confirm_delete.html'
    success_url = reverse_lazy('income-list')

    def get_queryset(self):
        return Income.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Income record deleted successfully!')
        return super().delete(request, *args, **kwargs)

# Expenses Views
class ExpensesListView(LoginRequiredMixin, ListView):
    model = Expenses
    template_name = 'tracker/expenses_list.html'
    context_object_name = 'expenses'

    def get_queryset(self):
        return Expenses.objects.filter(user=self.request.user)

class ExpensesCreateView(LoginRequiredMixin, CreateView):
    model = Expenses
    form_class = ExpensesForm
    template_name = 'tracker/expenses_form.html'
    success_url = reverse_lazy('expenses-list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Expense added successfully!')
        return super().form_valid(form)

class ExpensesUpdateView(LoginRequiredMixin, UpdateView):
    model = Expenses
    form_class = ExpensesForm
    template_name = 'tracker/expenses_form.html'
    success_url = reverse_lazy('expenses-list')

    def get_queryset(self):
        return Expenses.objects.filter(user=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, 'Expense updated successfully!')
        return super().form_valid(form)

class ExpensesDeleteView(LoginRequiredMixin, DeleteView):
    model = Expenses
    template_name = 'tracker/expenses_confirm_delete.html'
    success_url = reverse_lazy('expenses-list')

    def get_queryset(self):
        return Expenses.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Expense deleted successfully!')
        return super().delete(request, *args, **kwargs)

# NowNext Views
class NowNextListView(LoginRequiredMixin, ListView):
    model = NowNext
    template_name = 'tracker/nownext_list.html'
    context_object_name = 'nownexts'

    def get_queryset(self):
        return NowNext.objects.filter(user=self.request.user).order_by('-date')

class NowNextCreateView(LoginRequiredMixin, CreateView):
    model = NowNext
    form_class = NowNextForm
    template_name = 'tracker/nownext_form.html'
    success_url = reverse_lazy('nownext-list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Now & Next task created successfully!')
        return super().form_valid(form)

class NowNextUpdateView(LoginRequiredMixin, UpdateView):
    model = NowNext
    form_class = NowNextForm
    template_name = 'tracker/nownext_form.html'
    success_url = reverse_lazy('nownext-list')

    def get_queryset(self):
        return NowNext.objects.filter(user=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, 'Now & Next task updated successfully!')
        return super().form_valid(form)

class NowNextDeleteView(LoginRequiredMixin, DeleteView):
    model = NowNext
    template_name = 'tracker/nownext_confirm_delete.html'
    success_url = reverse_lazy('nownext-list')

    def get_queryset(self):
        return NowNext.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Now & Next task deleted successfully!')
        return super().delete(request, *args, **kwargs)

# Projects Views
class ProjectsListView(LoginRequiredMixin, ListView):
    model = Projects
    template_name = 'tracker/projects_list.html'
    context_object_name = 'projects'

    def get_queryset(self):
        return Projects.objects.filter(user=self.request.user)

class ProjectsCreateView(LoginRequiredMixin, CreateView):
    model = Projects
    form_class = ProjectsForm
    template_name = 'tracker/projects_form.html'
    success_url = reverse_lazy('projects-list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Project created successfully!')
        return super().form_valid(form)

class ProjectsUpdateView(LoginRequiredMixin, UpdateView):
    model = Projects
    form_class = ProjectsForm
    template_name = 'tracker/projects_form.html'
    success_url = reverse_lazy('projects-list')

    def get_queryset(self):
        return Projects.objects.filter(user=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, 'Project updated successfully!')
        return super().form_valid(form)

class ProjectsDeleteView(LoginRequiredMixin, DeleteView):
    model = Projects
    template_name = 'tracker/projects_confirm_delete.html'
    success_url = reverse_lazy('projects-list')

    def get_queryset(self):
        return Projects.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Project deleted successfully!')
        return super().delete(request, *args, **kwargs)

# Goals Views
class GoalsListView(LoginRequiredMixin, ListView):
    model = Goals
    template_name = 'tracker/goals_list.html'
    context_object_name = 'goals'

    def get_queryset(self):
        return Goals.objects.filter(user=self.request.user)

class GoalsCreateView(LoginRequiredMixin, CreateView):
    model = Goals
    form_class = GoalsForm
    template_name = 'tracker/goals_form.html'
    success_url = reverse_lazy('goals-list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Goal created successfully!')
        return super().form_valid(form)

class GoalsUpdateView(LoginRequiredMixin, UpdateView):
    model = Goals
    form_class = GoalsForm
    template_name = 'tracker/goals_form.html'
    success_url = reverse_lazy('goals-list')

    def get_queryset(self):
        return Goals.objects.filter(user=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, 'Goal updated successfully!')
        return super().form_valid(form)

class GoalsDeleteView(LoginRequiredMixin, DeleteView):
    model = Goals
    template_name = 'tracker/goals_confirm_delete.html'
    success_url = reverse_lazy('goals-list')

    def get_queryset(self):
        return Goals.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Goal deleted successfully!')
        return super().delete(request, *args, **kwargs)

# Event Views
class EventListView(LoginRequiredMixin, ListView):
    model = Event
    template_name = 'tracker/event_list.html'
    context_object_name = 'events'

    def get_queryset(self):
        return Event.objects.filter(user=self.request.user).order_by('start_date')

class EventCreateView(LoginRequiredMixin, CreateView):
    model = Event
    form_class = EventForm
    template_name = 'tracker/event_form.html'
    success_url = reverse_lazy('event-list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Event created successfully!')
        return super().form_valid(form)

class EventUpdateView(LoginRequiredMixin, UpdateView):
    model = Event
    form_class = EventForm
    template_name = 'tracker/event_form.html'
    success_url = reverse_lazy('event-list')

    def get_queryset(self):
        return Event.objects.filter(user=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, 'Event updated successfully!')
        return super().form_valid(form)

class EventDeleteView(LoginRequiredMixin, DeleteView):
    model = Event
    template_name = 'tracker/event_confirm_delete.html'
    success_url = reverse_lazy('event-list')

    def get_queryset(self):
        return Event.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Event deleted successfully!')
        return super().delete(request, *args, **kwargs)