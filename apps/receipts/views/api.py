from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import HttpResponse
from apps.common.soft_delete import SoftDeleteViewSetMixin, soft_delete_schema_view
from apps.common.tenancy import TenantQuerysetMixin, require_tenant_access, resolve_company_id, require_tenant_user
from apps.receipts.models import Receipt, ReceiptService, ReceiptItem
from apps.receipts.serializers.api import ReceiptSerializer, ReceiptServiceSerializer, ReceiptItemSerializer
from apps.receipts.services import calculate_receipt_totals, add_payment_to_receipt
from apps.common.services.pdf_service import PDFService
from apps.users.permissions import IsAdministrator, IsSecretary, IsCustomer, IsTenantUser
from config.s3_presign import presigned_url_for_file_field

@soft_delete_schema_view()
class ReceiptViewSet(SoftDeleteViewSetMixin, TenantQuerysetMixin, viewsets.ModelViewSet):
    queryset = Receipt.all_objects.all().prefetch_related("services", "items", "payments")
    serializer_class = ReceiptSerializer

    def get_permissions(self):
        base = [IsTenantUser()]
        if self.action == "hard_delete":
            return base + [IsAdministrator()]
        if self.request.user.is_authenticated and self.request.user.role == "CUSTOMER":
            return base + [IsCustomer()]
        return base + [(IsAdministrator | IsSecretary)()]

    def get_queryset(self):
        require_tenant_access(self.request, write=False)
        queryset = Receipt.all_objects.filter(
            company_id=resolve_company_id(self.request)
        ).prefetch_related("services", "items", "payments")
        user = self.request.user
        if user.role == "CUSTOMER":
            if hasattr(user, "customer_profile"):
                queryset = queryset.filter(customer=user.customer_profile)
            else:
                queryset = queryset.none()
        if self.action == "restore":
            return queryset.filter(deleted_at__isnull=False)
        if self.action == "hard_delete":
            return queryset
        return self.apply_deleted_filter(queryset)

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
        receipt.refresh_from_db()
        return Response({
            "detail": "PDF persisted",
            "url": presigned_url_for_file_field(receipt.pdf_file) or None,
        })

@soft_delete_schema_view()
class ReceiptServiceViewSet(SoftDeleteViewSetMixin, viewsets.ModelViewSet):
    queryset = ReceiptService.all_objects.all()
    serializer_class = ReceiptServiceSerializer

    def get_permissions(self):
        if self.action == "hard_delete":
            return [IsTenantUser(), IsAdministrator()]
        return [IsTenantUser(), (IsAdministrator | IsSecretary)()]

    def get_queryset(self):
        require_tenant_access(self.request, write=False)
        qs = ReceiptService.all_objects.filter(
            receipt__company_id=resolve_company_id(self.request)
        )
        if self.action == "restore":
            return qs.filter(deleted_at__isnull=False)
        if self.action == "hard_delete":
            return qs
        return self.apply_deleted_filter(qs)

    def perform_create(self, serializer):
        require_tenant_user(self.request.user)
        service = serializer.validated_data["service"]
        instance = serializer.save(
            name_snapshot=service.name,
            description_snapshot=service.description,
            unit_price=serializer.validated_data.get("unit_price", service.base_price)
        )
        calculate_receipt_totals(instance.receipt)

    def perform_update(self, serializer):
        require_tenant_user(self.request.user)
        instance = serializer.save()
        calculate_receipt_totals(instance.receipt)

    def perform_destroy(self, instance):
        require_tenant_user(self.request.user)
        receipt = instance.receipt
        instance.delete()
        calculate_receipt_totals(receipt)

@soft_delete_schema_view()
class ReceiptItemViewSet(SoftDeleteViewSetMixin, viewsets.ModelViewSet):
    queryset = ReceiptItem.all_objects.all()
    serializer_class = ReceiptItemSerializer

    def get_permissions(self):
        if self.action == "hard_delete":
            return [IsTenantUser(), IsAdministrator()]
        return [IsTenantUser(), (IsAdministrator | IsSecretary)()]

    def get_queryset(self):
        require_tenant_access(self.request, write=False)
        qs = ReceiptItem.all_objects.filter(
            receipt__company_id=resolve_company_id(self.request)
        )
        if self.action == "restore":
            return qs.filter(deleted_at__isnull=False)
        if self.action == "hard_delete":
            return qs
        return self.apply_deleted_filter(qs)

    def perform_create(self, serializer):
        require_tenant_user(self.request.user)
        instance = serializer.save()
        calculate_receipt_totals(instance.receipt)

    def perform_update(self, serializer):
        require_tenant_user(self.request.user)
        instance = serializer.save()
        calculate_receipt_totals(instance.receipt)

    def perform_destroy(self, instance):
        require_tenant_user(self.request.user)
        receipt = instance.receipt
        instance.delete()
        calculate_receipt_totals(receipt)
