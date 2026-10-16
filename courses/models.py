from django.conf import settings
from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"


class Course(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending Approval"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"

    class CourseType(models.TextChoices):
        FREE = "FREE", "Free"
        PAID = "PAID", "Paid"

    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="courses")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name="courses")
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    thumbnail = models.ImageField(upload_to="course_thumbnails/", blank=True, null=True)
    course_type = models.CharField(max_length=10, choices=CourseType.choices, default=CourseType.FREE)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Course.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        if self.course_type == self.CourseType.FREE:
            self.price = 0
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Section(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="sections")
    title = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class Lesson(models.Model):
    class LessonType(models.TextChoices):
        VIDEO = "VIDEO", "Video"
        PDF = "PDF", "PDF/Notes"
        ASSIGNMENT = "ASSIGNMENT", "Assignment"

    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name="lessons")
    title = models.CharField(max_length=255)
    lesson_type = models.CharField(max_length=12, choices=LessonType.choices, default=LessonType.VIDEO)
    video_file = models.FileField(upload_to="lesson_videos/", blank=True, null=True)
    video_url = models.URLField(blank=True, null=True, help_text="Or paste an external video URL")
    pdf_file = models.FileField(upload_to="lesson_notes/", blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    is_preview = models.BooleanField(default=False, help_text="Free preview lesson, visible without purchase")

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.title


class Enrollment(models.Model):
    class PaymentStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        PAID = "PAID", "Paid"
        FAILED = "FAILED", "Failed"

    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="enrollments")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="enrollments")
    payment_status = models.CharField(max_length=10, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    enrolled_date = models.DateTimeField(auto_now_add=True)
    progress_percent = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ("student", "course")

    def __str__(self):
        return f"{self.student.username} -> {self.course.title}"


class LessonProgress(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name="lesson_progress")
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        unique_together = ("enrollment", "lesson")
