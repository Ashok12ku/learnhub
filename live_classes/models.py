from django.conf import settings
from django.db import models
from django.utils import timezone

from courses.models import Course


class LiveClass(models.Model):
    class Platform(models.TextChoices):
        ZOOM = "ZOOM", "Zoom"
        GMEET = "GMEET", "Google Meet"
        OTHER = "OTHER", "Other"

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="live_classes")
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="live_classes")
    title = models.CharField(max_length=255)
    platform = models.CharField(max_length=10, choices=Platform.choices, default=Platform.ZOOM)
    meeting_link = models.URLField()
    scheduled_at = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField(default=60)
    notes = models.TextField(blank=True, null=True, help_text="Optional notes/agenda for students")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["scheduled_at"]

    def __str__(self):
        return f"{self.title} - {self.course.title} ({self.scheduled_at})"

    @property
    def end_time(self):
        return self.scheduled_at + timezone.timedelta(minutes=self.duration_minutes)

    @property
    def is_upcoming(self):
        return self.scheduled_at > timezone.now()

    @property
    def is_live_now(self):
        now = timezone.now()
        return self.scheduled_at <= now <= self.end_time

    @property
    def is_past(self):
        return timezone.now() > self.end_time

    @property
    def status_label(self):
        if self.is_live_now:
            return "LIVE"
        elif self.is_upcoming:
            return "UPCOMING"
        else:
            return "ENDED"
