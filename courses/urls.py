from django.urls import path
from . import views

app_name = "courses"

urlpatterns = [
    # Public
    path("courses/", views.course_list, name="course_list"),
    path("courses/<slug:slug>/", views.course_detail, name="course_detail"),
    path("courses/<slug:slug>/enroll-free/", views.enroll_free, name="enroll_free"),
    path("courses/<slug:slug>/lesson/<int:lesson_id>/", views.lesson_view, name="lesson_view"),
    path("courses/<slug:slug>/lesson/<int:lesson_id>/complete/", views.mark_lesson_complete, name="mark_lesson_complete"),

    # Teacher
    path("teacher/courses/", views.teacher_course_list, name="teacher_course_list"),
    path("teacher/courses/create/", views.create_course, name="create_course"),
    path("teacher/courses/<slug:slug>/edit/", views.edit_course, name="edit_course"),
    path("teacher/courses/<slug:slug>/builder/", views.course_builder, name="course_builder"),
    path("teacher/courses/<slug:slug>/section/<int:section_id>/add-lesson/", views.add_lesson, name="add_lesson"),
    path("teacher/courses/<slug:slug>/section/<int:section_id>/delete/", views.delete_section, name="delete_section"),
    path("teacher/courses/<slug:slug>/lesson/<int:lesson_id>/delete/", views.delete_lesson, name="delete_lesson"),
]
