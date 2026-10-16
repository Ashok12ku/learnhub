from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, StudentProfile, TeacherProfile


class CustomUserAdmin(UserAdmin):
    list_display = ("username", "email", "role", "is_approved", "is_staff")
    list_filter = ("role", "is_approved")
    fieldsets = UserAdmin.fieldsets + (
        ("LearnHub Info", {"fields": ("role", "phone", "bio", "profile_picture", "is_approved")}),
    )
    actions = ["approve_teachers"]

    def approve_teachers(self, request, queryset):
        queryset.update(is_approved=True)
    approve_teachers.short_description = "Approve selected teachers"


admin.site.register(User, CustomUserAdmin)
admin.site.register(StudentProfile)
admin.site.register(TeacherProfile)
