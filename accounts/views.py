from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect

from .forms import StudentSignUpForm, TeacherSignUpForm, LoginForm, ProfileUpdateForm
from .models import User
from courses.models import Course


def home(request):
    context = {
        "course_count": Course.objects.filter(status=Course.Status.APPROVED).count(),
        "student_count": User.objects.filter(role=User.Role.STUDENT).count(),
        "teacher_count": User.objects.filter(
            role=User.Role.TEACHER,
            is_approved=True,
        ).count(),
        "featured_courses": Course.objects.filter(
            status=Course.Status.APPROVED,
        ).select_related("teacher", "category").order_by("-created_at")[:3],
    }
    return render(request, "accounts/home.html", context)


def signup_choice(request):
    """Page asking: Signup as Student or Teacher?"""
    return render(request, "accounts/signup_choice.html")


def student_signup(request):
    if request.method == "POST":
        form = StudentSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Welcome to LearnHub! Your student account is ready.")
            return redirect("dashboard:student_dashboard")
    else:
        form = StudentSignUpForm()
    return render(request, "accounts/student_signup.html", {"form": form})


def teacher_signup(request):
    if request.method == "POST":
        form = TeacherSignUpForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Signup successful! Your teacher account is pending Admin approval. "
                "You will be able to log in once approved.",
            )
            return redirect("accounts:login")
    else:
        form = TeacherSignUpForm()
    return render(request, "accounts/teacher_signup.html", {"form": form})


def user_login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=username, password=password)
            if user is not None:
                if user.role == User.Role.TEACHER and not user.is_approved:
                    messages.error(request, "Your teacher account is still pending Admin approval.")
                    return redirect("accounts:login")
                login(request, user)
                return redirect_by_role(user)
            else:
                messages.error(request, "Invalid username or password.")
    else:
        form = LoginForm()
    return render(request, "accounts/login.html", {"form": form})


def redirect_by_role(user):
    if user.role == User.Role.ADMIN or user.is_superuser:
        return redirect("dashboard:admin_dashboard")
    elif user.role == User.Role.TEACHER:
        return redirect("dashboard:teacher_dashboard")
    else:
        return redirect("dashboard:student_dashboard")


@login_required
def user_logout(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("accounts:home")


@login_required
def profile(request):
    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("accounts:profile")
    else:
        form = ProfileUpdateForm(instance=request.user)
    return render(request, "accounts/profile.html", {"form": form})
