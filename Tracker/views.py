from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, TemplateView
from django.db.models.functions import TruncDate
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy
from django.db.models import Sum, Count
from datetime import datetime
from django.utils import timezone
from datetime import timedelta
from .models import *
from .forms import *
from django.db.models import Q
from django.contrib import messages
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
        daily_income = (
            Income.objects
            .filter(user=user, date__gte=thirty_days_ago)
            .annotate(day=TruncDate('date'))
            .values('day')
            .annotate(total=Sum('amount'))
            .order_by('day')
        )

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        total_worth = self.get_queryset().aggregate(Sum('worth'))['worth__sum'] or 0
        salary = IncomeSource.objects.filter(user=self.request.user, client="Monopoly").aggregate(Sum('worth'))['worth__sum'] or 0
        unique_clients = IncomeSource.objects.filter(user=self.request.user).values('client').distinct().count()
        print("------------------------->", total_worth)
        context.update({
            'salary': salary,
            'clients': unique_clients,
            'total_worth': total_worth,
        })
        return context

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

    def get_context_data(self, **kwargs):
        total_income = Income.objects.filter(user=self.request.user).aggregate(Sum('amount'))['amount__sum'] or 0
        context = super().get_context_data(**kwargs)
        context['total_income'] = total_income
        return context

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

    def get_context_data(self, **kwargs):
        import datetime
        from django.db.models import Sum
        from django.utils import timezone

        context = super().get_context_data(**kwargs)

        # Total expenses
        total_expenses = Expenses.objects.filter(user=self.request.user).aggregate(Sum('worth'))['worth__sum'] or 0

        # Monthly expenses
        this_month = timezone.now().month
        this_year = timezone.now().year
        monthly_expenses = Expenses.objects.filter(
            user=self.request.user,
            date__year=this_year,
            date__month=this_month
        ).aggregate(Sum('worth'))['worth__sum'] or 0

        # Average monthly expenses
        # First, get all months where there are expenses
        expenses_by_month = Expenses.objects.filter(user=self.request.user).annotate(
            month=models.functions.TruncMonth('date')
        ).values('month').annotate(
            monthly_total=Sum('worth')
        ).order_by('month')

        if expenses_by_month:
            avg_expenses = sum(item['monthly_total'] for item in expenses_by_month) / len(expenses_by_month)
        else:
            avg_expenses = 0

        # Data for Expense Trends Chart (Last 6 months)
        six_months_ago = timezone.now() - datetime.timedelta(days=180)
        recent_expenses = Expenses.objects.filter(
            user=self.request.user,
            date__gte=six_months_ago
        ).annotate(
            month=models.functions.TruncMonth('date')
        ).values('month').annotate(
            total=Sum('worth')
        ).order_by('month')

        # Prepare chart data
        months = []
        monthly_totals = []
        for expense in recent_expenses:
            months.append(expense['month'].strftime('%b %Y'))
            monthly_totals.append(float(expense['total']))

        # Data for Category Distribution (simple categorization based on name keywords)
        categories = ['Business', 'Personal', 'Investment', 'Food']
        category_data = []

        # Simple categorization logic (you might want to improve this)
        business_keywords = ['business', 'office', 'work', 'company', 'client']
        personal_keywords = ['personal', 'home', 'family', 'shopping', 'food']
        investment_keywords = ['investment', 'stock', 'crypto', 'property', 'asset']

        business_total = Expenses.objects.filter(
            user=self.request.user,
            category='BUSINESS'
        ).aggregate(Sum('worth'))['worth__sum'] or 0

        personal_total = Expenses.objects.filter(
            user=self.request.user,
            category='PERSONAL'
        ).aggregate(Sum('worth'))['worth__sum'] or 0

        investment_total = Expenses.objects.filter(
            user=self.request.user,
            category='INVESTMENT'
        ).aggregate(Sum('worth'))['worth__sum'] or 0
        food_total = Expenses.objects.filter(
            user=self.request.user,
            category='FOOD'
        ).aggregate(Sum('worth'))['worth__sum'] or 0

        category_data = [
            float(business_total),
            float(personal_total),
            float(investment_total),
            float(food_total)
        ]

        context.update({
            'total_expenses': total_expenses,
            'monthly_expenses': monthly_expenses,
            'avg_expenses': avg_expenses,
            'budget': 85.94,
            'chart_months': months,
            'chart_monthly_totals': monthly_totals,
            'chart_categories': categories,
            'chart_category_data': category_data,
            'business_total': business_total,
            'personal_total': personal_total,
            'investment_total': investment_total,
            'food_total': food_total,
        })

        return context

class ExpenseContextMixin:
    """Mixin to add expense context data to views."""

    def get_expense_context(self):
        """Get shared expense context data."""
        now = timezone.now()
        month_expenses = Expenses.objects.filter(
            user=self.request.user,
            date__year=now.year,
            date__month=now.month
        ).aggregate(Sum('worth'))['worth__sum'] or 0

        days_in_month = datetime.now().day
        daily_avg = month_expenses / days_in_month if days_in_month > 0 else 0

        budget = 85.27  # configurable per user
        budget_remaining = budget - month_expenses
        budget_percentage = (month_expenses / budget * 100) if budget > 0 else 0

        recent_expenses = Expenses.objects.filter(
            user=self.request.user
        ).order_by('-date')[:5]

        categories = ['BUSINESS', 'PERSONAL', 'INVESTMENT', 'FOOD']
        category_stats = {}
        for category in categories:
            total = Expenses.objects.filter(
                user=self.request.user,
                category=category
            ).aggregate(Sum('worth'))['worth__sum'] or 0
            category_stats[category] = total

        total_all = sum(category_stats.values())
        category_percentages = {}
        for category, total in category_stats.items():
            category_percentages[category] = (total / total_all * 100) if total_all > 0 else 0

        return {
            'month_expenses': month_expenses,
            'daily_avg': daily_avg,
            'budget': budget,
            'budget_remaining': budget_remaining,
            'budget_percentage': min(budget_percentage, 100),
            'recent_expenses': recent_expenses,
            'recent_count': recent_expenses.count(),
            'category_stats': category_stats,
            'category_percentages': category_percentages,
            'total_expenses': total_all,
        }

class ExpensesCreateView(LoginRequiredMixin, ExpenseContextMixin, CreateView):
    model = Expenses
    form_class = ExpensesForm
    template_name = 'tracker/expenses_form.html'
    success_url = reverse_lazy('expenses-list')

    def get_initial(self):
        """Set initial values for the form."""
        initial = super().get_initial()
        # Set default date to current time
        now = timezone.now()
        initial['date'] = now.strftime('%Y-%m-%dT%H:%M')
        return initial

    def form_valid(self, form):
        """Set the user before saving."""
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.get_expense_context())
        return context


class ExpensesUpdateView(LoginRequiredMixin, ExpenseContextMixin, UpdateView):
    model = Expenses
    form_class = ExpensesForm
    template_name = 'tracker/expenses_form.html'
    success_url = reverse_lazy('expenses-list')

    def get_queryset(self):
        return Expenses.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.get_expense_context())
        return context


class ExpensesDeleteView(LoginRequiredMixin, DeleteView):
    model = Expenses
    template_name = 'tracker/expenses_confirm_delete.html'
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

class DreamCarListView(LoginRequiredMixin, ListView):
    model = DreamCar
    template_name = 'dreamcar/dreamcar_list.html'
    context_object_name = 'cars'
    paginate_by = 12

    def get_queryset(self):
        queryset = DreamCar.objects.filter(user=self.request.user).order_by('-date_added')

        # Filter by status
        status = self.request.GET.get('status')
        if status == 'bought':
            queryset = queryset.filter(bought=True)
        elif status == 'not_bought':
            queryset = queryset.filter(bought=False)

        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(brand__icontains=search_query) |
                Q(model__icontains=search_query) |
                Q(description__icontains=search_query)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get the first picture for each car
        cars_with_first_picture = []
        for car in context['cars']:
            first_picture = car.pictures.first()  # Get first picture from ManyToMany
            cars_with_first_picture.append({
                'car': car,
                'first_picture': first_picture
            })

        context['cars_with_images'] = cars_with_first_picture
        context['total_cars'] = self.get_queryset().count()
        context['bought_cars'] = self.get_queryset().filter(bought=True).count()
        context['dream_cars'] = self.get_queryset().filter(bought=False).count()

        # Calculate total value
        total_value = sum(car.price for car in self.get_queryset().filter(bought=True))
        context['total_value'] = total_value

        return context

class DreamCarCreateView(LoginRequiredMixin, CreateView):
    model = DreamCar
    form_class = DreamCarForm
    template_name = 'dreamcar/dreamcar_form.html'
    success_url = reverse_lazy('dreamcar-list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, 'Dream car added successfully!')
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['picture_form'] = PictureForm()
        return context

class DreamCarUpdateView(LoginRequiredMixin, UpdateView):
    model = DreamCar
    form_class = DreamCarForm
    template_name = 'dreamcar/dreamcar_form.html'
    success_url = reverse_lazy('dreamcar-list')

    def get_queryset(self):
        return DreamCar.objects.filter(user=self.request.user)

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Dream car updated successfully!')
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['picture_form'] = PictureForm()
        return context

class DreamCarDeleteView(LoginRequiredMixin, DeleteView):
    model = DreamCar
    template_name = 'dreamcar/dreamcar_confirm_delete.html'
    success_url = reverse_lazy('dreamcar-list')

    def get_queryset(self):
        return DreamCar.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Dream car deleted successfully!')
        return super().delete(request, *args, **kwargs)

class DreamCarDetailView(LoginRequiredMixin, DetailView):
    model = DreamCar
    template_name = 'dreamcar/dreamcar_detail.html'
    context_object_name = 'car'

    def get_queryset(self):
        return DreamCar.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        car = self.get_object()

        # Get all pictures for this car
        context['pictures'] = car.pictures.all()

        # Get statistics
        context['total_cars'] = DreamCar.objects.filter(user=self.request.user).count()
        context['bought_cars'] = DreamCar.objects.filter(user=self.request.user, bought=True).count()

        # Calculate similar cars (same brand or similar price range)
        similar_cars = DreamCar.objects.filter(
            user=self.request.user
        ).exclude(
            pk=car.pk
        ).filter(
            Q(brand=car.brand) | Q(price__range=(car.price * 0.8, car.price * 1.2))
        )[:4]

        context['similar_cars'] = similar_cars

        return context

class AddPictureView(LoginRequiredMixin, CreateView):
    model = Pictures
    form_class = PictureForm
    template_name = 'dreamcar/add_picture.html'

    def form_valid(self, form):
        response = super().form_valid(form)

        # Get the car and add the picture to it
        car_id = self.kwargs.get('car_id')
        car = get_object_or_404(DreamCar, pk=car_id, user=self.request.user)
        car.pictures.add(self.object)

        messages.success(self.request, 'Picture added successfully!')
        return response

    def get_success_url(self):
        return reverse_lazy('dreamcar-detail', kwargs={'pk': self.kwargs.get('car_id')})

class DeletePictureView(LoginRequiredMixin, DeleteView):
    model = Pictures
    template_name = 'dreamcar/delete_picture.html'

    def get_success_url(self):
        car_id = self.kwargs.get('car_id')
        return reverse_lazy('dreamcar-detail', kwargs={'pk': car_id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        car_id = self.kwargs.get('car_id')
        car = get_object_or_404(DreamCar, pk=car_id, user=self.request.user)

        context['car'] = car
        context['car_id'] = car_id
        context['total_pictures'] = car.pictures.count()
        context['remaining_pictures'] = context['total_pictures'] - 1
        context['other_pictures'] = car.pictures.exclude(pk=self.object.pk)

        return context

    def delete(self, request, *args, **kwargs):
        # Remove the picture from the car's ManyToMany relationship
        car_id = self.kwargs.get('car_id')
        car = get_object_or_404(DreamCar, pk=car_id, user=self.request.user)
        picture = self.get_object()
        car.pictures.remove(picture)

        messages.success(request, 'Picture removed successfully!')
        return super().delete(request, *args, **kwargs)