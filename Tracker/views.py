from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, TemplateView
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
from .models import *
from .forms import *
import json

# Dashboard View
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

        # Expenses by category (simulated - you'd need categories in your model)
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
        return super().form_valid(form)

class IncomeSourceUpdateView(LoginRequiredMixin, UpdateView):
    model = IncomeSource
    form_class = IncomeSourceForm
    template_name = 'tracker/incomesource_form.html'
    success_url = reverse_lazy('incomesource-list')

    def get_queryset(self):
        return IncomeSource.objects.filter(user=self.request.user)

class IncomeSourceDeleteView(LoginRequiredMixin, DeleteView):
    model = IncomeSource
    template_name = 'tracker/incomesource_confirm_delete.html'
    success_url = reverse_lazy('incomesource-list')

    def get_queryset(self):
        return IncomeSource.objects.filter(user=self.request.user)

# Income Views
class IncomeListView(LoginRequiredMixin, ListView):
    model = Income
    template_name = 'tracker/income_list.html'
    context_object_name = 'incomes'

    def get_queryset(self):
        return Income.objects.filter(user=self.request.user)

class IncomeCreateView(LoginRequiredMixin, CreateView):
    model = Income
    form_class = IncomeForm
    template_name = 'tracker/income_form.html'
    success_url = reverse_lazy('income-list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Calculate stats
        from django.db.models import Avg, Sum
        from django.utils import timezone
        from datetime import timedelta

        # Monthly average income
        monthly_avg = Income.objects.filter(user=user).aggregate(
            avg=Avg('amount')
        )['avg'] or 0

        # Current month total
        start_of_month = timezone.now().replace(
            day=1, hour=0, minute=0, second=0, microsecond=0
        )
        month_total = Income.objects.filter(
            user=user,
            date__gte=start_of_month
        ).aggregate(Sum('amount'))['amount__sum'] or 0

        # Recent incomes
        recent_incomes = Income.objects.filter(user=user).order_by('-date')[:5]

        context.update({
            'monthly_avg': monthly_avg,
            'month_total': month_total,
            'income_goal': 5000,  # You can make this dynamic from user settings
            'recent_incomes': recent_incomes,
            'recent_count': Income.objects.filter(user=user).count(),
        })

        return context

class IncomeUpdateView(LoginRequiredMixin, UpdateView):
    model = Income
    form_class = IncomeForm
    template_name = 'tracker/income_form.html'
    success_url = reverse_lazy('income-list')

    def get_queryset(self):
        return Income.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Calculate stats
        from django.db.models import Avg, Sum
        from django.utils import timezone
        from datetime import timedelta

        # Monthly average income
        monthly_avg = Income.objects.filter(user=user).aggregate(
            avg=Avg('amount')
        )['avg'] or 0

        # Current month total
        start_of_month = timezone.now().replace(
            day=1, hour=0, minute=0, second=0, microsecond=0
        )
        month_total = Income.objects.filter(
            user=user,
            date__gte=start_of_month
        ).aggregate(Sum('amount'))['amount__sum'] or 0

        # Recent incomes
        recent_incomes = Income.objects.filter(user=user).order_by('-date')[:5]

        context.update({
            'monthly_avg': monthly_avg,
            'month_total': month_total,
            'income_goal': 5000,  # You can make this dynamic from user settings
            'recent_incomes': recent_incomes,
            'recent_count': Income.objects.filter(user=user).count(),
        })

        return context

class IncomeDeleteView(LoginRequiredMixin, DeleteView):
    model = Income
    template_name = 'tracker/income_confirm_delete.html'
    success_url = reverse_lazy('income-list')

    def get_queryset(self):
        return Income.objects.filter(user=self.request.user)

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
        return super().form_valid(form)

class ExpensesUpdateView(LoginRequiredMixin, UpdateView):
    model = Expenses
    form_class = ExpensesForm
    template_name = 'tracker/expenses_form.html'
    success_url = reverse_lazy('expenses-list')

    def get_queryset(self):
        return Expenses.objects.filter(user=self.request.user)

class ExpensesDeleteView(LoginRequiredMixin, DeleteView):
    model = Expenses
    template_name = 'tracker/expenses_confirm_delete.html'
    success_url = reverse_lazy('expenses-list')

    def get_queryset(self):
        return Expenses.objects.filter(user=self.request.user)

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
        return super().form_valid(form)

class NowNextUpdateView(LoginRequiredMixin, UpdateView):
    model = NowNext
    form_class = NowNextForm
    template_name = 'tracker/nownext_form.html'
    success_url = reverse_lazy('nownext-list')

    def get_queryset(self):
        return NowNext.objects.filter(user=self.request.user)

class NowNextDeleteView(LoginRequiredMixin, DeleteView):
    model = NowNext
    template_name = 'tracker/nownext_confirm_delete.html'
    success_url = reverse_lazy('nownext-list')

    def get_queryset(self):
        return NowNext.objects.filter(user=self.request.user)

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
        return super().form_valid(form)

class ProjectsUpdateView(LoginRequiredMixin, UpdateView):
    model = Projects
    form_class = ProjectsForm
    template_name = 'tracker/projects_form.html'
    success_url = reverse_lazy('projects-list')

    def get_queryset(self):
        return Projects.objects.filter(user=self.request.user)

class ProjectsDeleteView(LoginRequiredMixin, DeleteView):
    model = Projects
    template_name = 'tracker/projects_confirm_delete.html'
    success_url = reverse_lazy('projects-list')

    def get_queryset(self):
        return Projects.objects.filter(user=self.request.user)

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
        return super().form_valid(form)

class GoalsUpdateView(LoginRequiredMixin, UpdateView):
    model = Goals
    form_class = GoalsForm
    template_name = 'tracker/goals_form.html'
    success_url = reverse_lazy('goals-list')

    def get_queryset(self):
        return Goals.objects.filter(user=self.request.user)

class GoalsDeleteView(LoginRequiredMixin, DeleteView):
    model = Goals
    template_name = 'tracker/goals_confirm_delete.html'
    success_url = reverse_lazy('goals-list')

    def get_queryset(self):
        return Goals.objects.filter(user=self.request.user)

# Event Views
class EventListView(LoginRequiredMixin, ListView):
    model = Event
    template_name = 'tracker/event_list.html'
    context_object_name = 'events'

    def get_queryset(self):
        return Event.objects.filter(user=self.request.user).order_by('start_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        now = timezone.now()

        # Get all events for the current user
        events = Event.objects.filter(user=user)

        # Calculate stats
        context['upcoming_count'] = events.filter(start_date__gte=now).count()
        context['attended_count'] = events.filter(attended=True).count()
        context['month_count'] = events.filter(
            start_date__year=now.year,
            start_date__month=now.month
        ).count()
        context['hackathon_count'] = events.filter(category='Hackathon').count()

        # Get upcoming events (next 30 days)
        thirty_days_later = now + timedelta(days=30)
        context['upcoming_events'] = events.filter(
            start_date__range=[now, thirty_days_later]
        ).order_by('start_date')

        # Get past events
        context['past_events'] = events.filter(
            start_date__lt=now
        ).order_by('-start_date')

        # Add current date for calendar
        context['current_date'] = now
        context['now'] = now

        return context

class EventCreateView(LoginRequiredMixin, CreateView):
    model = Event
    form_class = EventForm
    template_name = 'tracker/event_form.html'
    success_url = reverse_lazy('event-list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class EventUpdateView(LoginRequiredMixin, UpdateView):
    model = Event
    form_class = EventForm
    template_name = 'tracker/event_form.html'
    success_url = reverse_lazy('event-list')

    def get_queryset(self):
        return Event.objects.filter(user=self.request.user)

class EventDeleteView(LoginRequiredMixin, DeleteView):
    model = Event
    template_name = 'tracker/event_confirm_delete.html'
    success_url = reverse_lazy('event-list')

    def get_queryset(self):
        return Event.objects.filter(user=self.request.user)


@method_decorator(csrf_exempt, name='dispatch')
class MarkEventAttendedView(LoginRequiredMixin, View):
    def post(self, request, pk):
        try:
            event = Event.objects.get(pk=pk, user=request.user)
            event.attended = True
            event.save()
            return JsonResponse({'success': True})
        except Event.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Event not found'})
