from django.urls import path
from . import views

app_name = "certificates"

urlpatterns = [
    path("my-certificates/", views.my_certificates, name="my_certificates"),
    path("certificates/<uuid:certificate_id>/download/", views.download_certificate, name="download_certificate"),
    path("verify-certificate/", views.verify_certificate, name="verify_certificate"),
]
