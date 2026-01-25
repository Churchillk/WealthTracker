from django.contrib import admin
from . models import *

# Register your models here.


admin.site.register(EmergencyFunds)
admin.site.register(IncomeGoal)
admin.site.register(IncomeSource)
admin.site.register(Income)

@admin.register(Expenses)
class ExpensesAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "user",
        "category",
        "worth",
        "date",
    )

    list_filter = (
        "category",
        "user",
        "date",
    )

    search_fields = (
        "name",
        "description",
        "user__username",
        "user__email",
    )

    ordering = ("-date",)

    date_hierarchy = "date"

    list_per_page = 25

    autocomplete_fields = ("user",)

    fieldsets = (
        ("Basic Info", {
            "fields": ("user", "name", "category", "worth"),
        }),
        ("Details", {
            "fields": ("description",),
        }),
        ("Metadata", {
            "fields": ("date",),
        }),
    )
    
admin.site.register(NowNext)
admin.site.register(Projects)
admin.site.register(Goals)
admin.site.register(Event)
admin.site.register(DreamCar)
admin.site.register(Pictures)