import io
from django.core.files.base import ContentFile
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas

from .models import Certificate


def generate_certificate_pdf(certificate):
    """Render a certificate PDF for the given Certificate instance and attach it to pdf_file."""
    buffer = io.BytesIO()
    page_size = landscape(A4)
    width, height = page_size
    c = canvas.Canvas(buffer, pagesize=page_size)

    navy = HexColor("#0d1b3e")
    gold = HexColor("#c9a227")

    # Border
    c.setStrokeColor(navy)
    c.setLineWidth(6)
    c.rect(1 * cm, 1 * cm, width - 2 * cm, height - 2 * cm)
    c.setStrokeColor(gold)
    c.setLineWidth(2)
    c.rect(1.4 * cm, 1.4 * cm, width - 2.8 * cm, height - 2.8 * cm)

    # Header
    c.setFillColor(navy)
    c.setFont("Helvetica-Bold", 30)
    c.drawCentredString(width / 2, height - 3.2 * cm, "LearnHub")

    c.setFont("Helvetica", 16)
    c.setFillColor(HexColor("#444444"))
    c.drawCentredString(width / 2, height - 4.1 * cm, "Certificate of Completion")

    # Body
    c.setFont("Helvetica", 14)
    c.drawCentredString(width / 2, height - 6.5 * cm, "This is to certify that")

    student_name = certificate.student.get_full_name() or certificate.student.username
    c.setFont("Helvetica-Bold", 26)
    c.setFillColor(navy)
    c.drawCentredString(width / 2, height - 8.2 * cm, student_name)

    c.setFont("Helvetica", 14)
    c.setFillColor(HexColor("#444444"))
    c.drawCentredString(width / 2, height - 9.8 * cm, "has successfully completed the course")

    c.setFont("Helvetica-Bold", 20)
    c.setFillColor(gold)
    c.drawCentredString(width / 2, height - 11.2 * cm, certificate.course.title)

    c.setFont("Helvetica", 11)
    c.setFillColor(HexColor("#444444"))
    c.drawCentredString(
        width / 2, height - 12.7 * cm,
        f"Instructor: {certificate.course.teacher.get_full_name() or certificate.course.teacher.username}"
    )

    # Footer: date + verification
    c.setFont("Helvetica", 10)
    c.drawString(
        2.2 * cm, 2.2 * cm,
        f"Issued on: {certificate.issued_at.strftime('%d %B %Y')}"
    )
    c.drawRightString(
        width - 2.2 * cm, 2.2 * cm,
        f"Verification Code: {certificate.verification_code}"
    )

    c.showPage()
    c.save()

    buffer.seek(0)
    filename = f"certificate_{certificate.verification_code}.pdf"
    certificate.pdf_file.save(filename, ContentFile(buffer.read()), save=True)
    return certificate


def issue_certificate_if_eligible(enrollment):
    """Call this whenever progress updates. Issues a certificate once progress hits 100%."""
    if enrollment.progress_percent < 100:
        return None

    certificate, created = Certificate.objects.get_or_create(
        student=enrollment.student, course=enrollment.course
    )
    if created or not certificate.pdf_file:
        generate_certificate_pdf(certificate)
    return certificate
