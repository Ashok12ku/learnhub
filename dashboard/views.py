from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum
from django.contrib import messages

from .decorators import role_required
from courses.models import Course, Enrollment
from accounts.models import User


# =========================
# STUDENT DASHBOARD
# =========================

@login_required
@role_required("STUDENT")
def student_dashboard(request):
    enrollments = Enrollment.objects.filter(
        student=request.user,
        payment_status="PAID"
    )

    context = {
        "enrollments": enrollments,
        "total_courses": enrollments.count(),
    }

    return render(
        request,
        "dashboard/student_dashboard.html",
        context
    )


# =========================
# TEACHER DASHBOARD
# =========================

@login_required
@role_required("TEACHER")
def teacher_dashboard(request):
    courses = Course.objects.filter(
        teacher=request.user
    )

    total_students = Enrollment.objects.filter(
        course__teacher=request.user,
        payment_status="PAID"
    ).values(
        "student"
    ).distinct().count()

    total_earning = Enrollment.objects.filter(
        course__teacher=request.user,
        payment_status="PAID"
    ).aggregate(
        total=Sum("course__price")
    )["total"] or 0

    context = {
        "courses": courses,
        "total_courses": courses.count(),
        "total_students": total_students,
        "total_earning": total_earning,
    }

    return render(
        request,
        "dashboard/teacher_dashboard.html",
        context
    )


# =========================
# ADMIN DASHBOARD
# =========================

@login_required
@role_required("ADMIN")
def admin_dashboard(request):

    pending_teachers = User.objects.filter(
        role=User.Role.TEACHER,
        is_approved=False
    ).order_by("-created_at")

    pending_courses = Course.objects.filter(
        status=Course.Status.PENDING
    ).select_related(
        "teacher",
        "category"
    ).order_by("-created_at")

    context = {

        # Students
        "total_students": User.objects.filter(
            role=User.Role.STUDENT
        ).count(),

        # Teachers
        "total_teachers": User.objects.filter(
            role=User.Role.TEACHER
        ).count(),

        # Pending teachers
        "pending_teachers": pending_teachers.count(),
        "pending_teacher_list": pending_teachers,

        # Courses
        "total_courses": Course.objects.count(),

        "pending_courses": pending_courses.count(),

        "pending_course_list": pending_courses,

        # Revenue
        "total_revenue": Enrollment.objects.filter(
            payment_status=Enrollment.PaymentStatus.PAID
        ).aggregate(
            total=Sum("course__price")
        )["total"] or 0,
    }

    return render(
        request,
        "dashboard/admin_dashboard.html",
        context
    )


# =========================
# APPROVE TEACHER
# =========================

@login_required
@role_required("ADMIN")
def approve_teacher(request, user_id):

    if request.method == "POST":

        teacher = get_object_or_404(
            User,
            id=user_id,
            role=User.Role.TEACHER
        )

        teacher.is_approved = True

        teacher.save(
            update_fields=["is_approved"]
        )

        messages.success(
            request,
            f"Teacher {teacher.username} has been approved."
        )

    return redirect(
        "dashboard:admin_dashboard"
    )


# =========================
# REJECT TEACHER
# =========================

@login_required
@role_required("ADMIN")
def reject_teacher(request, user_id):

    if request.method == "POST":

        teacher = get_object_or_404(
            User,
            id=user_id,
            role=User.Role.TEACHER
        )

        teacher.is_approved = False

        teacher.save(
            update_fields=["is_approved"]
        )

        messages.warning(
            request,
            f"Teacher {teacher.username} has been rejected."
        )

    return redirect(
        "dashboard:admin_dashboard"
    )


# =========================
# APPROVE COURSE
# =========================

@login_required
@role_required("ADMIN")
def approve_course(request, course_id):

    if request.method == "POST":

        course = get_object_or_404(
            Course,
            id=course_id,
            status=Course.Status.PENDING
        )

        course.status = Course.Status.APPROVED

        course.save(
            update_fields=["status", "updated_at"]
        )

        messages.success(
            request,
            f'Course "{course.title}" has been approved.'
        )

    return redirect(
        "dashboard:admin_dashboard"
    )


# =========================
# REJECT COURSE
# =========================

@login_required
@role_required("ADMIN")
def reject_course(request, course_id):

    if request.method == "POST":

        course = get_object_or_404(
            Course,
            id=course_id,
            status=Course.Status.PENDING
        )

        course.status = Course.Status.REJECTED

        course.save(
            update_fields=["status", "updated_at"]
        )

        messages.warning(
            request,
            f'Course "{course.title}" has been rejected.'
        )

    return redirect(
        "dashboard:admin_dashboard"
    )