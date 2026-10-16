from django.urls import path
from . import views

app_name = "exams"

urlpatterns = [
    # Teacher
    path("teacher/courses/<slug:slug>/tests/", views.teacher_test_list, name="teacher_test_list"),
    path("teacher/courses/<slug:slug>/tests/create/", views.create_test, name="create_test"),
    path("teacher/courses/<slug:slug>/tests/<int:test_id>/questions/", views.manage_questions, name="manage_questions"),
    path("teacher/courses/<slug:slug>/tests/<int:test_id>/questions/<int:question_id>/delete/", views.delete_question, name="delete_question"),
    path("teacher/courses/<slug:slug>/tests/<int:test_id>/results/", views.test_results_overview, name="test_results_overview"),

    # Student
    path("courses/<slug:slug>/tests/", views.student_test_list, name="student_test_list"),
    path("courses/<slug:slug>/tests/<int:test_id>/take/", views.take_test, name="take_test"),
    path("courses/<slug:slug>/tests/<int:test_id>/submit/", views.submit_test, name="submit_test"),
    path("courses/<slug:slug>/tests/results/history/", views.result_history, name="result_history"),
    path("courses/<slug:slug>/tests/result/<int:result_id>/", views.result_detail, name="result_detail"),
]
