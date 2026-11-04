from django.contrib import admin
from .models import Category, Ticket



@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = (
        "id", "title", "category",
        "status", "owner", "created_at"
    )
    list_filter = ("status", "category")
    search_fields = ("title",)
