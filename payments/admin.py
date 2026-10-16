from django.contrib import admin
from .models import Order, Coupon


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ("code", "discount_percent", "valid_until", "times_used", "max_uses", "active")
    list_filter = ("active",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "student", "course", "final_price", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("student__username", "course__title", "razorpay_order_id")
