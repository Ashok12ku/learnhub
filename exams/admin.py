from django.contrib import admin
from .models import Test, Question, Result, StudentAnswer


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1


@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "duration_minutes", "pass_percentage", "is_active")
    inlines = [QuestionInline]


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ("student", "test", "percentage", "status", "submitted_at")
    list_filter = ("status",)


admin.site.register(Question)
admin.site.register(StudentAnswer)
