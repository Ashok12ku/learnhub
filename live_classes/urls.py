from django.urls import path
from . import views

app_name = "live_classes"

urlpatterns = [
    # Teacher
    path("teacher/courses/<slug:slug>/live-classes/", views.teacher_live_class_list, name="teacher_live_class_list"),
    path("teacher/courses/<slug:slug>/live-classes/schedule/", views.schedule_live_class, name="schedule_live_class"),
    path("teacher/courses/<slug:slug>/live-classes/<int:class_id>/edit/", views.edit_live_class, name="edit_live_class"),
    path("teacher/courses/<slug:slug>/live-classes/<int:class_id>/delete/", views.delete_live_class, name="delete_live_class"),

    # Student
    path("courses/<slug:slug>/live-classes/", views.student_live_class_list, name="student_live_class_list"),
    path("my-live-classes/", views.all_my_live_classes, name="all_my_live_classes"),
]
