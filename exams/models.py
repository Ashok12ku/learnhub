from django.conf import settings
from django.db import models
from django.utils import timezone

from courses.models import Course


class Test(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="tests")
    title = models.CharField(max_length=255)
    duration_minutes = models.PositiveIntegerField(default=30, help_text="Time limit for the test")
    pass_percentage = models.PositiveIntegerField(default=40)
    negative_marking = models.BooleanField(default=False)
    negative_marks_per_wrong = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    attempt_limit = models.PositiveIntegerField(default=1, help_text="How many times a student may attempt this test")
    randomize_questions = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.course.title})"

    @property
    def total_questions(self):
        return self.questions.count()

    @property
    def total_marks(self):
        return self.questions.count()  # 1 mark per question by default


class Question(models.Model):
    class Correct(models.TextChoices):
        A = "A", "Option A"
        B = "B", "Option B"
        C = "C", "Option C"
        D = "D", "Option D"

    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name="questions")
    question_text = models.TextField()
    option_a = models.CharField(max_length=500)
    option_b = models.CharField(max_length=500)
    option_c = models.CharField(max_length=500)
    option_d = models.CharField(max_length=500)
    correct_option = models.CharField(max_length=1, choices=Correct.choices)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.question_text[:60]

    def option_text(self, letter):
        return getattr(self, f"option_{letter.lower()}")


class Result(models.Model):
    class Status(models.TextChoices):
        PASSED = "PASSED", "Passed"
        FAILED = "FAILED", "Failed"

    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="test_results")
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name="results")
    attempt_number = models.PositiveIntegerField(default=1)

    total_questions = models.PositiveIntegerField()
    correct_count = models.PositiveIntegerField()
    wrong_count = models.PositiveIntegerField()
    unanswered_count = models.PositiveIntegerField(default=0)
    score = models.DecimalField(max_digits=6, decimal_places=2)
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    status = models.CharField(max_length=6, choices=Status.choices)

    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-submitted_at"]

    def __str__(self):
        return f"{self.student.username} - {self.test.title} - {self.percentage}%"


class StudentAnswer(models.Model):
    result = models.ForeignKey(Result, on_delete=models.CASCADE, related_name="answers")
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_option = models.CharField(max_length=1, blank=True, null=True)
    is_correct = models.BooleanField(default=False)
