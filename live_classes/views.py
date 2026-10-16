from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST

from dashboard.decorators import role_required
from courses.models import Course, Enrollment
from .models import LiveClass
from .forms import LiveClassForm


# ---------- TEACHER ----------

@login_required
@role_required("TEACHER")
def teacher_live_class_list(request, slug):
    course = get_object_or_404(Course, slug=slug, teacher=request.user)
    classes = course.live_classes.all()
    return render(request, "live_classes/teacher/class_list.html", {"course": course, "classes": classes})


@login_required
@role_required("TEACHER")
def schedule_live_class(request, slug):
    course = get_object_or_404(Course, slug=slug, teacher=request.user)
    if request.method == "POST":
        form = LiveClassForm(request.POST)
        if form.is_valid():
            live_class = form.save(commit=False)
            live_class.course = course
            live_class.teacher = request.user
            live_class.save()
            messages.success(request, "Live class scheduled! Enrolled students will see it on their dashboard.")
            return redirect("live_classes:teacher_live_class_list", slug=slug)
    else:
        form = LiveClassForm()
    return render(request, "live_classes/teacher/schedule_class.html", {"form": form, "course": course})


@login_required
@role_required("TEACHER")
def edit_live_class(request, slug, class_id):
    course = get_object_or_404(Course, slug=slug, teacher=request.user)
    live_class = get_object_or_404(LiveClass, id=class_id, course=course)
    if request.method == "POST":
        form = LiveClassForm(request.POST, instance=live_class)
        if form.is_valid():
            form.save()
            messages.success(request, "Live class updated.")
            return redirect("live_classes:teacher_live_class_list", slug=slug)
    else:
        form = LiveClassForm(instance=live_class)
    return render(request, "live_classes/teacher/schedule_class.html", {"form": form, "course": course, "live_class": live_class})


@login_required
@role_required("TEACHER")
@require_POST
def delete_live_class(request, slug, class_id):
    course = get_object_or_404(Course, slug=slug, teacher=request.user)
    LiveClass.objects.filter(id=class_id, course=course).delete()
    messages.success(request, "Live class cancelled/deleted.")
    return redirect("live_classes:teacher_live_class_list", slug=slug)


# ---------- STUDENT ----------

@login_required
@role_required("STUDENT")
def student_live_class_list(request, slug):
    course = get_object_or_404(Course, slug=slug, status=Course.Status.APPROVED)
    is_enrolled = Enrollment.objects.filter(
        student=request.user, course=course, payment_status=Enrollment.PaymentStatus.PAID
    ).exists()
    if not is_enrolled:
        messages.error(request, "You need to be enrolled in this course to view its live classes.")
        return redirect("courses:course_detail", slug=slug)

    classes = course.live_classes.all()
    upcoming = [c for c in classes if not c.is_past]
    past = [c for c in classes if c.is_past]

    return render(request, "live_classes/student/class_list.html", {
        "course": course, "upcoming": upcoming, "past": past,
    })


@login_required
@role_required("STUDENT")
def all_my_live_classes(request):
    """Cross-course dashboard view: all upcoming live classes across every enrolled course."""
    enrolled_course_ids = Enrollment.objects.filter(
        student=request.user, payment_status=Enrollment.PaymentStatus.PAID
    ).values_list("course_id", flat=True)

    classes = LiveClass.objects.filter(course_id__in=enrolled_course_ids).order_by("scheduled_at")
    upcoming = [c for c in classes if not c.is_past]

    return render(request, "live_classes/student/all_classes.html", {"upcoming": upcoming})
