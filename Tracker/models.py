from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

WALLETS = [
    ("Binance", "Binance"),
    ("M-pesa", "M-pesa"),
    ("TrustWallet", "TrustWallet"),
    ("Bank", "Bank"),
    ("Paypal", "Paypal"),
    ("Other", "Other"),
]

class EmergencyFunds(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.IntegerField(default=0)
    date_added = models.DateTimeField(default=timezone.now)
    wallet = models.CharField(max_length=100, choices=WALLETS, default="Bank")


class IncomeGoal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.IntegerField(default=0)
    by_when = models.DateTimeField(default=timezone.now)
    wallet = models.CharField(max_length=100, choices=WALLETS, default="Bank")

class IncomeSource(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, default="")
    client = models.CharField(max_length=100, default="")
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(default=timezone.now)
    worth = models.IntegerField(default=0)
    description = models.TextField(default="")

    def __str__(self):
        return f"{self.name} - {self.client}"

class Income(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    source = models.ForeignKey(IncomeSource, on_delete=models.CASCADE, null=True, blank=True)
    wallet = models.CharField(max_length=100, choices=WALLETS, default="Bank")
    amount = models.IntegerField(default=0)  # Added this field
    date = models.DateTimeField(default=timezone.now)
    description = models.TextField(default="")

    def __str__(self):
        return f"{self.amount} - {self.wallet}"

class Expenses(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, default="")
    worth = models.IntegerField(default=0)
    description = models.TextField(default="")
    date = models.DateTimeField(default=timezone.now)  # Added this field

    def __str__(self):
        return self.name

class NowNext(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now)
    do = models.TextField(default="")
    done = models.BooleanField(default=False)
    challenges = models.TextField(default="")
    gratitude = models.TextField(default="")

    def __str__(self):
        return f"{self.date.date()} - {'Done' if self.done else 'Pending'}"

class Projects(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    what_next = models.ForeignKey(NowNext, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100, default="")
    date_set = models.DateTimeField(default=timezone.now)
    description = models.TextField()
    end_date = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=[
        ('Planning', 'Planning'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
        ('On Hold', 'On Hold')
    ], default='Planning')

    def __str__(self):
        return self.name

class Goals(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    goal_title = models.CharField(max_length=100, default="")
    date_set = models.DateTimeField(default=timezone.now)
    goal_description = models.TextField()
    end_date = models.DateTimeField(default=timezone.now)
    achieved = models.BooleanField(default=False)

    def __str__(self):
        return self.goal_title

class Event(models.Model):
    EVENTS = [
        ("Hackathon", "hackathon"),
        ("AI", "ai"),
        ("Blockchain", "blockchain"),
        ("Cybersecurity", "cybersecurity"),
        ("Other", "other"),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100, default="")
    host = models.CharField(max_length=50)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(default=timezone.now)
    location = models.TextField(default="")
    category = models.CharField(max_length=50, default="Hackathon", choices=EVENTS)
    attended = models.BooleanField(default=False)

    def __str__(self):
        return self.title