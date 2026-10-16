from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("", views.home, name="home"),
    path("signup/", views.signup_choice, name="signup_choice"),
    path("signup/student/", views.student_signup, name="student_signup"),
    path("signup/teacher/", views.teacher_signup, name="teacher_signup"),
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
    path("profile/", views.profile, name="profile"),
]
