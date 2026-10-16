from django.urls import path
from . import views

app_name = "payments"

urlpatterns = [
    path("checkout/<slug:slug>/", views.checkout, name="checkout"),
    path("checkout/<slug:slug>/pay/", views.create_razorpay_order, name="create_razorpay_order"),
    path("payment-success/", views.payment_success, name="payment_success"),
    path("my-orders/", views.my_orders, name="my_orders"),
]
