from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.utils import timezone
from django.views.decorators.http import require_POST

from dashboard.decorators import role_required
from .models import Course, Category, Section, Lesson, Enrollment, LessonProgress
from .forms import CourseForm, SectionForm, LessonForm


def recompute_progress(enrollment):
    """Recalculate progress_percent for an enrollment based on completed lessons."""
    total_lessons = Lesson.objects.filter(section__course=enrollment.course).count()
    if total_lessons == 0:
        enrollment.progress_percent = 0
    else:
        completed = LessonProgress.objects.filter(enrollment=enrollment, completed=True).count()
        enrollment.progress_percent = round((completed / total_lessons) * 100)
    enrollment.save(update_fields=["progress_percent"])

    if enrollment.progress_percent >= 100:
        from certificates.generator import issue_certificate_if_eligible
        issue_certificate_if_eligible(enrollment)

    return enrollment.progress_percent


@login_required
@role_required("STUDENT")
@require_POST
def enroll_free(request, slug):
    course = get_object_or_404(Course, slug=slug, status=Course.Status.APPROVED)
    if course.course_type != Course.CourseType.FREE:
        messages.error(request, "This is a paid course. Please use Buy Now.")
        return redirect("courses:course_detail", slug=slug)

    enrollment, created = Enrollment.objects.get_or_create(
        student=request.user, course=course,
        defaults={"payment_status": Enrollment.PaymentStatus.PAID},
    )
    if not created and enrollment.payment_status != Enrollment.PaymentStatus.PAID:
        enrollment.payment_status = Enrollment.PaymentStatus.PAID
        enrollment.save()

    messages.success(request, f"You're enrolled in {course.title}! Start learning below.")
    return redirect("courses:course_detail", slug=slug)


@login_required
@role_required("STUDENT")
@require_POST
def mark_lesson_complete(request, slug, lesson_id):
    course = get_object_or_404(Course, slug=slug, status=Course.Status.APPROVED)
    lesson = get_object_or_404(Lesson, id=lesson_id, section__course=course)

    enrollment = Enrollment.objects.filter(
        student=request.user, course=course, payment_status=Enrollment.PaymentStatus.PAID
    ).first()

    if not enrollment:
        messages.error(request, "You need to be enrolled in this course to track progress.")
        return redirect("courses:course_detail", slug=slug)

    progress, _ = LessonProgress.objects.get_or_create(enrollment=enrollment, lesson=lesson)
    progress.completed = True
    progress.completed_at = timezone.now()
    progress.save()

    percent = recompute_progress(enrollment)
    messages.success(request, f"Lesson marked complete! Course progress: {percent}%")
    return redirect("courses:lesson_view", slug=slug, lesson_id=lesson_id)


# ---------- PUBLIC: Browse & Detail ----------

def course_list(request):
    courses = Course.objects.filter(status=Course.Status.APPROVED)

    query = request.GET.get("q")
    category_slug = request.GET.get("category")
    course_type = request.GET.get("type")

    if query:
        courses = courses.filter(Q(title__icontains=query) | Q(description__icontains=query))
    if category_slug:
        courses = courses.filter(category__slug=category_slug)
    if course_type in ["FREE", "PAID"]:
        courses = courses.filter(course_type=course_type)

    categories = Category.objects.all()
    context = {
        "courses": courses,
        "categories": categories,
        "query": query or "",
        "selected_category": category_slug or "",
        "selected_type": course_type or "",
    }
    return render(request, "courses/course_list.html", context)


def course_detail(request, slug):
    course = get_object_or_404(Course, slug=slug, status=Course.Status.APPROVED)
    is_enrolled = False
    enrollment = None
    completed_lesson_ids = []

    if request.user.is_authenticated and request.user.is_student:
        enrollment = Enrollment.objects.filter(
            student=request.user, course=course, payment_status=Enrollment.PaymentStatus.PAID
        ).first()
        if enrollment:
            is_enrolled = True
            completed_lesson_ids = list(
                LessonProgress.objects.filter(enrollment=enrollment, completed=True).values_list("lesson_id", flat=True)
            )

    context = {
        "course": course,
        "sections": course.sections.all(),
        "total_lessons": Lesson.objects.filter(section__course=course).count(),
        "is_enrolled": is_enrolled,
        "enrollment": enrollment,
        "completed_lesson_ids": completed_lesson_ids,
    }
    return render(request, "courses/course_detail.html", context)


@login_required
def lesson_view(request, slug, lesson_id):
    course = get_object_or_404(Course, slug=slug, status=Course.Status.APPROVED)
    lesson = get_object_or_404(Lesson, id=lesson_id, section__course=course)

    enrollment = None
    is_enrolled = False
    is_completed = False
    if request.user.is_student:
        enrollment = Enrollment.objects.filter(
            student=request.user, course=course, payment_status=Enrollment.PaymentStatus.PAID
        ).first()
        is_enrolled = enrollment is not None
        if enrollment:
            is_completed = LessonProgress.objects.filter(
                enrollment=enrollment, lesson=lesson, completed=True
            ).exists()

    if not (is_enrolled or lesson.is_preview or course.course_type == Course.CourseType.FREE):
        messages.error(request, "Please purchase this course to access this lesson.")
        return redirect("courses:course_detail", slug=slug)

    return render(request, "courses/lesson_view.html", {
        "course": course, "lesson": lesson, "is_enrolled": is_enrolled, "is_completed": is_completed,
    })


# ---------- TEACHER: Create & Manage Courses ----------

@login_required
@role_required("TEACHER")
def teacher_course_list(request):
    courses = Course.objects.filter(teacher=request.user)
    return render(request, "courses/teacher/course_list.html", {"courses": courses})


@login_required
@role_required("TEACHER")
def create_course(request):
    if not request.user.is_approved:
        messages.error(request, "Your account is pending Admin approval. You cannot create courses yet.")
        return redirect("dashboard:teacher_dashboard")

    if request.method == "POST":
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            course = form.save(commit=False)
            course.teacher = request.user
            course.status = Course.Status.PENDING
            course.save()
            messages.success(request, "Course created! Now add sections and lessons. It will go live after Admin approval.")
            return redirect("courses:course_builder", slug=course.slug)
    else:
        form = CourseForm()
    return render(request, "courses/teacher/create_course.html", {"form": form})


@login_required
@role_required("TEACHER")
def edit_course(request, slug):
    course = get_object_or_404(Course, slug=slug, teacher=request.user)
    if request.method == "POST":
        form = CourseForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            course = form.save(commit=False)
            course.status = Course.Status.PENDING  # re-approval needed after edit
            course.save()
            messages.success(request, "Course updated. It will need re-approval from Admin.")
            return redirect("courses:course_builder", slug=course.slug)
    else:
        form = CourseForm(instance=course)
    return render(request, "courses/teacher/create_course.html", {"form": form, "course": course})


@login_required
@role_required("TEACHER")
def course_builder(request, slug):
    """Add sections & lessons to a course."""
    course = get_object_or_404(Course, slug=slug, teacher=request.user)

    section_form = SectionForm()
    if request.method == "POST" and "add_section" in request.POST:
        section_form = SectionForm(request.POST)
        if section_form.is_valid():
            section = section_form.save(commit=False)
            section.course = course
            section.save()
            messages.success(request, "Section added.")
            return redirect("courses:course_builder", slug=slug)

    context = {
        "course": course,
        "sections": course.sections.all(),
        "section_form": section_form,
    }
    return render(request, "courses/teacher/course_builder.html", context)


@login_required
@role_required("TEACHER")
def add_lesson(request, slug, section_id):
    course = get_object_or_404(Course, slug=slug, teacher=request.user)
    section = get_object_or_404(Section, id=section_id, course=course)

    if request.method == "POST":
        form = LessonForm(request.POST, request.FILES)
        if form.is_valid():
            lesson = form.save(commit=False)
            lesson.section = section
            lesson.save()
            messages.success(request, "Lesson added.")
            return redirect("courses:course_builder", slug=slug)
    else:
        form = LessonForm()
    return render(request, "courses/teacher/add_lesson.html", {"form": form, "course": course, "section": section})


@login_required
@role_required("TEACHER")
@require_POST
def delete_section(request, slug, section_id):
    course = get_object_or_404(Course, slug=slug, teacher=request.user)
    Section.objects.filter(id=section_id, course=course).delete()
    messages.success(request, "Section deleted.")
    return redirect("courses:course_builder", slug=slug)


@login_required
@role_required("TEACHER")
@require_POST
def delete_lesson(request, slug, lesson_id):
    course = get_object_or_404(Course, slug=slug, teacher=request.user)
    Lesson.objects.filter(id=lesson_id, section__course=course).delete()
    messages.success(request, "Lesson deleted.")
    return redirect("courses:course_builder", slug=slug)
