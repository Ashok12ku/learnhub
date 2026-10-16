from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    # =========================
    # DASHBOARDS
    # =========================

    path(
        "student/",
        views.student_dashboard,
        name="student_dashboard"
    ),

    path(
        "teacher/",
        views.teacher_dashboard,
        name="teacher_dashboard"
    ),

    path(
        "admin/",
        views.admin_dashboard,
        name="admin_dashboard"
    ),

    # =========================
    # TEACHER APPROVAL
    # =========================

    path(
        "admin/teacher/<int:user_id>/approve/",
        views.approve_teacher,
        name="approve_teacher"
    ),

    path(
        "admin/teacher/<int:user_id>/reject/",
        views.reject_teacher,
        name="reject_teacher"
    ),

    # =========================
    # COURSE APPROVAL
    # =========================

    path(
        "admin/course/<int:course_id>/approve/",
        views.approve_course,
        name="approve_course"
    ),

    path(
        "admin/course/<int:course_id>/reject/",
        views.reject_course,
        name="reject_course"
    ),
]