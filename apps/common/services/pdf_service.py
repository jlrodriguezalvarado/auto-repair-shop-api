from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
from django.core.files.base import ContentFile

class PDFService:
    @staticmethod
    def generate_estimate_pdf(estimate, persist=False):
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)

        # Simple PDF Layout
        p.drawString(100, 750, f"Presupuesto: {estimate.code}")
        p.drawString(100, 730, f"Cliente: {estimate.customer.first_name} {estimate.customer.last_name}")
        p.drawString(100, 710, f"Vehículo: {estimate.vehicle.plate} - {estimate.vehicle.brand} {estimate.vehicle.model}")

        y = 680
        p.drawString(100, y, "Servicios:")
        y -= 20
        for service in estimate.services.all():
            p.drawString(120, y, f"- {service.name_snapshot}: {service.total_price}")
            y -= 20

        p.drawString(100, y-20, f"Total: {estimate.total}")

        p.showPage()
        p.save()

        buffer.seek(0)
        pdf_data = buffer.getvalue()

        if persist:
            estimate.pdf_file.save(f"estimate_{estimate.code}.pdf", ContentFile(pdf_data))

        return pdf_data

    @staticmethod
    def generate_receipt_pdf(receipt, persist=False):
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)

        p.drawString(100, 750, f"Recibo: {receipt.code}")
        p.drawString(100, 730, f"Cliente: {receipt.customer.first_name} {receipt.customer.last_name}")
        p.drawString(100, 710, f"Total: {receipt.total}")
        p.drawString(100, 690, f"Pagado: {receipt.paid_amount}")
        p.drawString(100, 670, f"Pendiente: {receipt.pending_amount}")

        p.showPage()
        p.save()

        buffer.seek(0)
        pdf_data = buffer.getvalue()

        if persist:
            receipt.pdf_file.save(f"receipt_{receipt.code}.pdf", ContentFile(pdf_data))

        return pdf_data
