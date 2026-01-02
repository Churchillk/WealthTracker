from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .forms import CustomUserCreationForm
from django.contrib.auth.views import LogoutView

urlpatterns = [
    # Dashboard
    path('', views.DashboardView.as_view(), name='dashboard'),

    # IncomeSource URLs
    path('incomesource/', views.IncomeSourceListView.as_view(), name='incomesource-list'),
    path('incomesource/new/', views.IncomeSourceCreateView.as_view(), name='incomesource-create'),
    path('incomesource/<int:pk>/edit/', views.IncomeSourceUpdateView.as_view(), name='incomesource-update'),
    path('incomesource/<int:pk>/delete/', views.IncomeSourceDeleteView.as_view(), name='incomesource-delete'),

    # Income URLs
    path('income/', views.IncomeListView.as_view(), name='income-list'),
    path('income/new/', views.IncomeCreateView.as_view(), name='income-create'),
    path('income/<int:pk>/edit/', views.IncomeUpdateView.as_view(), name='income-update'),
    path('income/<int:pk>/delete/', views.IncomeDeleteView.as_view(), name='income-delete'),

    # Expenses URLs
    path('expenses/', views.ExpensesListView.as_view(), name='expenses-list'),
    path('expenses/new/', views.ExpensesCreateView.as_view(), name='expenses-create'),
    path('expenses/<int:pk>/edit/', views.ExpensesUpdateView.as_view(), name='expenses-update'),
    path('expenses/<int:pk>/delete/', views.ExpensesDeleteView.as_view(), name='expenses-delete'),

    # NowNext URLs
    path('nownext/', views.NowNextListView.as_view(), name='nownext-list'),
    path('nownext/new/', views.NowNextCreateView.as_view(), name='nownext-create'),
    path('nownext/<int:pk>/edit/', views.NowNextUpdateView.as_view(), name='nownext-update'),
    path('nownext/<int:pk>/delete/', views.NowNextDeleteView.as_view(), name='nownext-delete'),

    # Projects URLs
    path('projects/', views.ProjectsListView.as_view(), name='projects-list'),
    path('projects/new/', views.ProjectsCreateView.as_view(), name='projects-create'),
    path('projects/<int:pk>/edit/', views.ProjectsUpdateView.as_view(), name='projects-update'),
    path('projects/<int:pk>/delete/', views.ProjectsDeleteView.as_view(), name='projects-delete'),

    # Goals URLs
    path('goals/', views.GoalsListView.as_view(), name='goals-list'),
    path('goals/new/', views.GoalsCreateView.as_view(), name='goals-create'),
    path('goals/<int:pk>/edit/', views.GoalsUpdateView.as_view(), name='goals-update'),
    path('goals/<int:pk>/delete/', views.GoalsDeleteView.as_view(), name='goals-delete'),

    # Event URLs
    path('events/', views.EventListView.as_view(), name='event-list'),
    path('events/new/', views.EventCreateView.as_view(), name='event-create'),
    path('events/<int:pk>/edit/', views.EventUpdateView.as_view(), name='event-update'),
    path('events/<int:pk>/delete/', views.EventDeleteView.as_view(), name='event-delete'),

    # DreamCar URLs
    path('dreamcars/', views.DreamCarListView.as_view(), name='dreamcar-list'),
    path('dreamcars/new/', views.DreamCarCreateView.as_view(), name='dreamcar-create'),
    path('dreamcars/<int:pk>/', views.DreamCarDetailView.as_view(), name='dreamcar-detail'),
    path('dreamcars/<int:pk>/edit/', views.DreamCarUpdateView.as_view(), name='dreamcar-update'),
    path('dreamcars/<int:pk>/delete/', views.DreamCarDeleteView.as_view(), name='dreamcar-delete'),
    path('dreamcars/<int:car_id>/add-picture/', views.AddPictureView.as_view(), name='dreamcar-add-picture'),
    path('dreamcars/<int:car_id>/pictures/<int:pk>/delete/', views.DeletePictureView.as_view(), name='dreamcar-delete-picture'),
]