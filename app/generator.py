from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, A4
from reportlab.pdfgen import canvas


CERTIFICATE_DIR = Path("certificates")

CERTIFICATE_DIR.mkdir(
    exist_ok=True
)


def generate_certificate(
    certificate_id: int,
    recipient_name: str,
    event_name: str,
    event_date: str,
    issuer_name: str
) -> str:

    file_path = (
        CERTIFICATE_DIR
        / f"certificate_{certificate_id}.pdf"
    )

    page_width, page_height = landscape(A4)

    pdf = canvas.Canvas(
        str(file_path),
        pagesize=(page_width, page_height)
    )

    # Outer border
    pdf.setStrokeColor(colors.darkblue)
    pdf.setLineWidth(4)

    pdf.rect(
        30,
        30,
        page_width - 60,
        page_height - 60
    )

    # Inner border
    pdf.setStrokeColor(colors.gold)
    pdf.setLineWidth(2)

    pdf.rect(
        45,
        45,
        page_width - 90,
        page_height - 90
    )

    # Certificate title
    pdf.setFillColor(colors.darkblue)

    pdf.setFont(
        "Helvetica-Bold",
        34
    )

    pdf.drawCentredString(
        page_width / 2,
        page_height - 120,
        "CERTIFICATE"
    )

    pdf.setFont(
        "Helvetica-Bold",
        20
    )

    pdf.drawCentredString(
        page_width / 2,
        page_height - 150,
        "OF PARTICIPATION"
    )

    # Introductory text
    pdf.setFillColor(colors.black)

    pdf.setFont(
        "Helvetica",
        16
    )

    pdf.drawCentredString(
        page_width / 2,
        page_height - 210,
        "This certificate is proudly presented to"
    )

    # Recipient name
    pdf.setFillColor(colors.darkblue)

    pdf.setFont(
        "Helvetica-Bold",
        28
    )

    pdf.drawCentredString(
        page_width / 2,
        page_height - 260,
        recipient_name
    )

    # Event text
    pdf.setFillColor(colors.black)

    pdf.setFont(
        "Helvetica",
        15
    )

    pdf.drawCentredString(
        page_width / 2,
        page_height - 310,
        "for successfully participating in"
    )

    # Event name
    pdf.setFillColor(colors.darkblue)

    pdf.setFont(
        "Helvetica-Bold",
        22
    )

    pdf.drawCentredString(
        page_width / 2,
        page_height - 345,
        event_name
    )

    # Date
    pdf.setFillColor(colors.black)

    pdf.setFont(
        "Helvetica",
        13
    )

    pdf.drawString(
        100,
        100,
        f"Date: {event_date}"
    )

    # Issuer
    pdf.drawRightString(
        page_width - 100,
        100,
        f"Issued by: {issuer_name}"
    )

    # Certificate ID
    pdf.setFont(
        "Helvetica",
        10
    )

    pdf.drawCentredString(
        page_width / 2,
        70,
        f"Certificate ID: {certificate_id}"
    )

    pdf.save()

    return str(file_path)