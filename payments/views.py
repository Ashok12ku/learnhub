import razorpay
from decimal import Decimal, ROUND_HALF_UP

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.utils import timezone

from courses.models import Course, Enrollment
from dashboard.decorators import role_required
from .models import Order, Coupon


def get_razorpay_client():
    return razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


@login_required
@role_required("STUDENT")
def checkout(request, slug):
    course = get_object_or_404(Course, slug=slug, status=Course.Status.APPROVED)

    if course.course_type == Course.CourseType.FREE:
        messages.info(request, "This course is free — no payment needed.")
        return redirect("courses:course_detail", slug=slug)

    already_enrolled = Enrollment.objects.filter(
        student=request.user, course=course, payment_status=Enrollment.PaymentStatus.PAID
    ).exists()
    if already_enrolled:
        messages.info(request, "You already own this course.")
        return redirect("courses:course_detail", slug=slug)

    final_price = course.price
    applied_coupon = None
    coupon_message = None

    if request.method == "POST" and "apply_coupon" in request.POST:
        code = request.POST.get("coupon_code", "").strip().upper()
        try:
            coupon = Coupon.objects.get(code=code)
            if coupon.is_valid():
                applied_coupon = coupon
                final_price = coupon.apply_discount(course.price).quantize(
                    Decimal("0.01"),
                    rounding=ROUND_HALF_UP,
                )
                coupon_message = f"Coupon applied! {coupon.discount_percent}% off."
            else:
                coupon_message = "This coupon has expired or is no longer valid."
        except Coupon.DoesNotExist:
            coupon_message = "Invalid coupon code."

        return render(request, "payments/checkout.html", {
            "course": course,
            "final_price": final_price,
            "applied_coupon": applied_coupon,
            "coupon_message": coupon_message,
            "coupon_code": code,
        })

    return render(request, "payments/checkout.html", {
        "course": course,
        "final_price": final_price,
        "coupon_code": "",
    })


@login_required
@role_required("STUDENT")
@require_POST
def create_razorpay_order(request, slug):
    """Called via the Pay Now button - creates a Razorpay order and our local Order record."""
    course = get_object_or_404(Course, slug=slug, status=Course.Status.APPROVED)
    already_enrolled = Enrollment.objects.filter(
        student=request.user, course=course, payment_status=Enrollment.PaymentStatus.PAID
    ).exists()
    if already_enrolled:
        messages.info(request, "You already own this course.")
        return redirect("courses:course_detail", slug=slug)

    coupon_code = request.POST.get("coupon_code", "").strip().upper()
    coupon = None
    final_price = course.price
    if coupon_code:
        coupon = Coupon.objects.filter(code=coupon_code).first()
        if coupon and coupon.is_valid():
            final_price = coupon.apply_discount(course.price).quantize(
                Decimal("0.01"),
                rounding=ROUND_HALF_UP,
            )
        else:
            coupon = None
            messages.error(request, "This coupon is invalid or no longer available.")
            return redirect("payments:checkout", slug=slug)

    amount_paise = int(final_price * 100)  # Razorpay expects amount in paise

    client = get_razorpay_client()
    try:
        rzp_order = client.order.create({
            "amount": amount_paise,
            "currency": "INR",
            "payment_capture": 1,
        })
    except Exception as e:
        messages.error(request, "Could not connect to payment gateway. Please try again.")
        return redirect("payments:checkout", slug=slug)

    order = Order.objects.create(
        student=request.user,
        course=course,
        coupon=coupon,
        original_price=course.price,
        final_price=final_price,
        razorpay_order_id=rzp_order["id"],
        status=Order.Status.CREATED,
    )

    context = {
        "course": course,
        "order": order,
        "razorpay_key_id": settings.RAZORPAY_KEY_ID,
        "amount_paise": amount_paise,
        "student_email": request.user.email,
        "student_name": request.user.get_full_name() or request.user.username,
    }
    return render(request, "payments/razorpay_checkout.html", context)


@login_required
@role_required("STUDENT")
def payment_success(request):
    """Razorpay redirects/posts here after checkout.js payment. We verify the signature."""
    order_id = request.POST.get("razorpay_order_id") or request.GET.get("razorpay_order_id")
    payment_id = request.POST.get("razorpay_payment_id") or request.GET.get("razorpay_payment_id")
    signature = request.POST.get("razorpay_signature") or request.GET.get("razorpay_signature")

    order = get_object_or_404(Order, razorpay_order_id=order_id, student=request.user)

    client = get_razorpay_client()
    params_dict = {
        "razorpay_order_id": order_id,
        "razorpay_payment_id": payment_id,
        "razorpay_signature": signature,
    }

    try:
        client.utility.verify_payment_signature(params_dict)
        verified = True
    except razorpay.errors.SignatureVerificationError:
        verified = False

    if verified:
        order.razorpay_payment_id = payment_id
        order.razorpay_signature = signature
        order.status = Order.Status.PAID
        order.paid_at = timezone.now()
        order.save()

        if order.coupon:
            order.coupon.times_used += 1
            order.coupon.save()

        Enrollment.objects.update_or_create(
            student=request.user, course=order.course,
            defaults={"payment_status": Enrollment.PaymentStatus.PAID},
        )
        messages.success(request, f"Payment successful! You now have access to {order.course.title}.")
        return redirect("courses:course_detail", slug=order.course.slug)
    else:
        order.status = Order.Status.FAILED
        order.save()
        messages.error(request, "Payment verification failed. Please contact support if money was deducted.")
        return redirect("payments:checkout", slug=order.course.slug)


@login_required
@role_required("STUDENT")
def my_orders(request):
    orders = Order.objects.filter(student=request.user).order_by("-created_at")
    return render(request, "payments/my_orders.html", {"orders": orders})
