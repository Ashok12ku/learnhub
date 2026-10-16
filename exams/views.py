import random
from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST

from dashboard.decorators import role_required
from courses.models import Course, Enrollment
from .models import Test, Question, Result, StudentAnswer
from .forms import TestForm, QuestionForm


# ---------- TEACHER ----------

@login_required
@role_required("TEACHER")
def teacher_test_list(request, slug):
    course = get_object_or_404(Course, slug=slug, teacher=request.user)
    tests = course.tests.all()
    return render(request, "exams/teacher/test_list.html", {"course": course, "tests": tests})


@login_required
@role_required("TEACHER")
def create_test(request, slug):
    course = get_object_or_404(Course, slug=slug, teacher=request.user)
    if request.method == "POST":
        form = TestForm(request.POST)
        if form.is_valid():
            test = form.save(commit=False)
            test.course = course
            test.save()
            messages.success(request, "Test created! Now add questions.")
            return redirect("exams:manage_questions", slug=slug, test_id=test.id)
    else:
        form = TestForm()
    return render(request, "exams/teacher/create_test.html", {"form": form, "course": course})


@login_required
@role_required("TEACHER")
def manage_questions(request, slug, test_id):
    course = get_object_or_404(Course, slug=slug, teacher=request.user)
    test = get_object_or_404(Test, id=test_id, course=course)

    if request.method == "POST":
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.test = test
            question.save()
            messages.success(request, "Question added.")
            return redirect("exams:manage_questions", slug=slug, test_id=test.id)
    else:
        form = QuestionForm()

    return render(request, "exams/teacher/manage_questions.html", {
        "course": course, "test": test, "form": form, "questions": test.questions.all(),
    })


@login_required
@role_required("TEACHER")
@require_POST
def delete_question(request, slug, test_id, question_id):
    course = get_object_or_404(Course, slug=slug, teacher=request.user)
    test = get_object_or_404(Test, id=test_id, course=course)
    Question.objects.filter(id=question_id, test=test).delete()
    messages.success(request, "Question deleted.")
    return redirect("exams:manage_questions", slug=slug, test_id=test.id)


@login_required
@role_required("TEACHER")
def test_results_overview(request, slug, test_id):
    course = get_object_or_404(Course, slug=slug, teacher=request.user)
    test = get_object_or_404(Test, id=test_id, course=course)
    results = test.results.select_related("student").all()
    return render(request, "exams/teacher/test_results.html", {"course": course, "test": test, "results": results})


# ---------- STUDENT ----------

@login_required
@role_required("STUDENT")
def student_test_list(request, slug):
    course = get_object_or_404(Course, slug=slug, status=Course.Status.APPROVED)
    is_enrolled = Enrollment.objects.filter(
        student=request.user, course=course, payment_status=Enrollment.PaymentStatus.PAID
    ).exists()
    if not is_enrolled:
        messages.error(request, "You need to be enrolled in this course to take its tests.")
        return redirect("courses:course_detail", slug=slug)

    tests = course.tests.filter(is_active=True)
    test_data = []
    for t in tests:
        attempts_used = Result.objects.filter(student=request.user, test=t).count()
        test_data.append({
            "test": t,
            "attempts_used": attempts_used,
            "attempts_left": max(t.attempt_limit - attempts_used, 0),
            "can_attempt": attempts_used < t.attempt_limit,
        })

    return render(request, "exams/student/test_list.html", {
        "course": course, "test_data": test_data,
    })


@login_required
@role_required("STUDENT")
def take_test(request, slug, test_id):
    course = get_object_or_404(Course, slug=slug, status=Course.Status.APPROVED)
    test = get_object_or_404(Test, id=test_id, course=course, is_active=True)

    is_enrolled = Enrollment.objects.filter(
        student=request.user, course=course, payment_status=Enrollment.PaymentStatus.PAID
    ).exists()
    if not is_enrolled:
        messages.error(request, "You need to be enrolled in this course to take its tests.")
        return redirect("courses:course_detail", slug=slug)

    attempts_used = Result.objects.filter(student=request.user, test=test).count()
    if attempts_used >= test.attempt_limit:
        messages.error(request, "You have used all your attempts for this test.")
        return redirect("exams:student_test_list", slug=slug)

    questions = list(test.questions.all())
    if test.randomize_questions:
        random.shuffle(questions)

    context = {
        "course": course,
        "test": test,
        "questions": questions,
        "duration_seconds": test.duration_minutes * 60,
    }
    return render(request, "exams/student/take_test.html", context)


@login_required
@role_required("STUDENT")
def submit_test(request, slug, test_id):
    course = get_object_or_404(Course, slug=slug, status=Course.Status.APPROVED)
    test = get_object_or_404(Test, id=test_id, course=course, is_active=True)

    if request.method != "POST":
        return redirect("exams:take_test", slug=slug, test_id=test_id)

    attempts_used = Result.objects.filter(student=request.user, test=test).count()
    if attempts_used >= test.attempt_limit:
        messages.error(request, "You have used all your attempts for this test.")
        return redirect("exams:student_test_list", slug=slug)

    questions = test.questions.all()
    correct_count = 0
    wrong_count = 0
    unanswered_count = 0
    answers_to_save = []

    for question in questions:
        selected = request.POST.get(f"question_{question.id}")
        if not selected:
            unanswered_count += 1
            answers_to_save.append((question, None, False))
            continue
        is_correct = (selected == question.correct_option)
        if is_correct:
            correct_count += 1
        else:
            wrong_count += 1
        answers_to_save.append((question, selected, is_correct))

    total_questions = questions.count()
    score = Decimal(correct_count)
    if test.negative_marking:
        score -= Decimal(wrong_count) * test.negative_marks_per_wrong
    score = max(score, Decimal("0"))

    percentage = (score / total_questions * 100) if total_questions else Decimal("0")
    percentage = round(percentage, 2)
    status = Result.Status.PASSED if percentage >= test.pass_percentage else Result.Status.FAILED

    result = Result.objects.create(
        student=request.user, test=test, attempt_number=attempts_used + 1,
        total_questions=total_questions, correct_count=correct_count, wrong_count=wrong_count,
        unanswered_count=unanswered_count, score=score, percentage=percentage, status=status,
    )

    StudentAnswer.objects.bulk_create([
        StudentAnswer(result=result, question=q, selected_option=sel, is_correct=corr)
        for q, sel, corr in answers_to_save
    ])

    return redirect("exams:result_detail", slug=slug, result_id=result.id)


@login_required
@role_required("STUDENT")
def result_detail(request, slug, result_id):
    result = get_object_or_404(Result, id=result_id, student=request.user)
    answers = result.answers.select_related("question").all()
    return render(request, "exams/student/result_detail.html", {"result": result, "answers": answers})


@login_required
@role_required("STUDENT")
def result_history(request, slug):
    course = get_object_or_404(Course, slug=slug)
    results = Result.objects.filter(student=request.user, test__course=course)
    return render(request, "exams/student/result_history.html", {"course": course, "results": results})
