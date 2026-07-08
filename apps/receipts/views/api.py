from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import HttpResponse
from apps.receipts.models import Receipt, ReceiptService, ReceiptItem, ReceiptPayment
from apps.receipts.serializers.api import ReceiptSerializer, ReceiptServiceSerializer, ReceiptItemSerializer, ReceiptPaymentSerializer
from apps.receipts.services import calculate_receipt_totals, add_payment_to_receipt
from apps.common.services.pdf_service import PDFService
from apps.users.permissions import IsAdministrator, IsSecretary, IsCustomer

class ReceiptViewSet(viewsets.ModelViewSet):
    queryset = Receipt.objects.all().prefetch_related("services", "items", "payments")
    serializer_class = ReceiptSerializer

    def get_permissions(self):
        if self.request.user.role == "CUSTOMER":
            return [IsCustomer()]
        return [(IsAdministrator | IsSecretary)()]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.role == "CUSTOMER":
            if hasattr(user, 'customer_profile'):
                return queryset.filter(customer=user.customer_profile)
            return queryset.none()
        return queryset

    @action(detail=True, methods=["post"])
    def add_payment(self, request, pk=None):
        receipt = self.get_object()
        amount = request.data.get("amount")
        payment_method = request.data.get("payment_method")
        reference = request.data.get("reference")
        notes = request.data.get("notes")

        try:
            add_payment_to_receipt(receipt, amount, payment_method, reference, notes)
            return Response(ReceiptSerializer(receipt).data)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["get"])
    def pdf(self, request, pk=None):
        receipt = self.get_object()
        persist = request.query_params.get("persist", "false").lower() == "true"
        pdf_data = PDFService.generate_receipt_pdf(receipt, persist=persist)
        response = HttpResponse(pdf_data, content_type="application/pdf")
        response["Content-Disposition"] = f'inline; filename="receipt_{receipt.code}.pdf"'
        return response

    @action(detail=True, methods=["post"])
    def persist_pdf(self, request, pk=None):
        receipt = self.get_object()
        PDFService.generate_receipt_pdf(receipt, persist=True)
        return Response({"detail": "PDF persisted", "url": receipt.pdf_file.url if receipt.pdf_file else None})


class ReceiptServiceViewSet(viewsets.ModelViewSet):
    queryset = ReceiptService.objects.all()
    serializer_class = ReceiptServiceSerializer
    permission_classes = [IsAdministrator | IsSecretary]

    def perform_create(self, serializer):
        service = serializer.validated_data['service']
        instance = serializer.save(
            name_snapshot=service.name,
            description_snapshot=service.description,
            unit_price=serializer.validated_data.get('unit_price', service.base_price)
        )
        calculate_receipt_totals(instance.receipt)

class ReceiptItemViewSet(viewsets.ModelViewSet):
    queryset = ReceiptItem.objects.all()
    serializer_class = ReceiptItemSerializer
    permission_classes = [IsAdministrator | IsSecretary]

    def perform_create(self, serializer):
        instance = serializer.save()
        calculate_receipt_totals(instance.receipt)
