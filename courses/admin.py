from django.contrib import admin
from .models import Category, Course, Section, Lesson, Enrollment, LessonProgress


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1


class SectionInline(admin.TabularInline):
    model = Section
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "teacher", "category", "course_type", "price", "status")
    list_filter = ("status", "course_type", "category")
    inlines = [SectionInline]
    actions = ["approve_courses", "reject_courses"]

    def approve_courses(self, request, queryset):
        queryset.update(status=Course.Status.APPROVED)
    approve_courses.short_description = "Approve selected courses"

    def reject_courses(self, request, queryset):
        queryset.update(status=Course.Status.REJECTED)
    reject_courses.short_description = "Reject selected courses"


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "order")
    inlines = [LessonInline]


admin.site.register(Lesson)
admin.site.register(Enrollment)
admin.site.register(LessonProgress)
