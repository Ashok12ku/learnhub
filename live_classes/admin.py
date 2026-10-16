from django.contrib import admin
from .models import LiveClass


@admin.register(LiveClass)
class LiveClassAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "teacher", "platform", "scheduled_at", "duration_minutes")
    list_filter = ("platform", "course")
