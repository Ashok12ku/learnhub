from decimal import Decimal
from django.conf import settings
from django.db import models
from django.utils import timezone

from courses.models import Course


class Coupon(models.Model):
    code = models.CharField(max_length=30, unique=True)
    discount_percent = models.PositiveIntegerField(help_text="e.g. 20 for 20% off")
    valid_from = models.DateTimeField(default=timezone.now)
    valid_until = models.DateTimeField()
    max_uses = models.PositiveIntegerField(default=100)
    times_used = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.code} ({self.discount_percent}% off)"

    def is_valid(self):
        now = timezone.now()
        return (
            self.active
            and self.valid_from <= now <= self.valid_until
            and self.times_used < self.max_uses
        )

    def apply_discount(self, price):
        discount = (Decimal(self.discount_percent) / Decimal(100)) * price
        return max(price - discount, Decimal("0"))


class Order(models.Model):
    class Status(models.TextChoices):
        CREATED = "CREATED", "Created"
        PAID = "PAID", "Paid"
        FAILED = "FAILED", "Failed"

    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="orders")
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)

    original_price = models.DecimalField(max_digits=8, decimal_places=2)
    final_price = models.DecimalField(max_digits=8, decimal_places=2)

    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=255, blank=True, null=True)

    status = models.CharField(max_length=10, choices=Status.choices, default=Status.CREATED)
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Order #{self.id} - {self.student.username} - {self.course.title} ({self.status})"
