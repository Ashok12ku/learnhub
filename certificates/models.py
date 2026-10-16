import uuid

from django.conf import settings
from django.db import models

from courses.models import Course


class Certificate(models.Model):
    certificate_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    verification_code = models.CharField(max_length=8, unique=True, editable=False, blank=True)
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="certificates")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="certificates")
    pdf_file = models.FileField(upload_to="certificates/", blank=True, null=True)
    issued_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("student", "course")

    def save(self, *args, **kwargs):
        if not self.verification_code:
            self.verification_code = str(self.certificate_id)[:8].upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Certificate: {self.student.username} - {self.course.title}"
