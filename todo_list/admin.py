from django.contrib import admin
from .models import Task

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "user",
        "important",
        "completed",
        "created_at",
        "due_date",
    )

    search_fields = (
        "title",
        "user__username",
    )

    list_filter = (
        "important",
        "completed",
        "created_at",
    )
