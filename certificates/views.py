from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404

from dashboard.decorators import role_required
from .models import Certificate


@login_required
@role_required("STUDENT")
def my_certificates(request):
    certs = Certificate.objects.filter(student=request.user)
    return render(request, "certificates/my_certificates.html", {"certificates": certs})


@login_required
@role_required("STUDENT")
def download_certificate(request, certificate_id):
    cert = get_object_or_404(Certificate, certificate_id=certificate_id, student=request.user)
    if not cert.pdf_file:
        messages.error(request, "Certificate file not ready yet. Please try again shortly.")
        return redirect("certificates:my_certificates")
    return redirect(cert.pdf_file.url)


def verify_certificate(request):
    """Public page: anyone can verify a certificate by its short verification code."""
    code = request.GET.get("code", "").strip().upper()
    certificate = None
    searched = False

    if code:
        searched = True
        certificate = Certificate.objects.filter(verification_code=code).first()

    return render(request, "certificates/verify.html", {
        "certificate": certificate, "code": code, "searched": searched,
    })
