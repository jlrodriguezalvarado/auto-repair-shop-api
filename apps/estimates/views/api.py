from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import HttpResponse
from apps.common.soft_delete import SoftDeleteViewSetMixin, soft_delete_schema_view
from apps.common.tenancy import TenantQuerysetMixin, require_tenant_access, resolve_company_id, require_tenant_user
from apps.estimates.models import Estimate, EstimateService, EstimateItem
from apps.estimates.serializers.api import EstimateSerializer, EstimateServiceSerializer, EstimateItemSerializer
from apps.estimates.services import calculate_estimate_totals, create_work_order_from_estimate
from apps.common.services.pdf_service import PDFService
from apps.users.permissions import IsAdministrator, IsSecretary, IsCustomer, IsTenantUser
from config.s3_presign import presigned_url_for_file_field

@soft_delete_schema_view()
class EstimateViewSet(SoftDeleteViewSetMixin, TenantQuerysetMixin, viewsets.ModelViewSet):
    queryset = Estimate.all_objects.all().prefetch_related("services", "items")
    serializer_class = EstimateSerializer

    def get_permissions(self):
        base = [IsTenantUser()]
        if self.action == "hard_delete":
            return base + [IsAdministrator()]
        if self.request.user.is_authenticated and self.request.user.role == "CUSTOMER":
            return base + [IsCustomer()]
        return base + [(IsAdministrator | IsSecretary)()]

    def get_queryset(self):
        require_tenant_access(self.request, write=False)
        queryset = Estimate.all_objects.filter(
            company_id=resolve_company_id(self.request)
        ).prefetch_related("services", "items")
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
    def approve(self, request, pk=None):
        estimate = self.get_object()
        estimate.status = Estimate.Status.APPROVED
        estimate.save()
        calculate_estimate_totals(estimate)
        from apps.notifications.services.domain_events import notify_estimate_approved
        notify_estimate_approved(estimate, actor=request.user)
        return Response(EstimateSerializer(estimate).data)

    @action(detail=True, methods=["post"])
    def create_work_order(self, request, pk=None):
        estimate = self.get_object()
        try:
            work_order = create_work_order_from_estimate(estimate)
            return Response({"detail": "Work order created", "work_order_id": work_order.id})
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["get"])
    def pdf(self, request, pk=None):
        estimate = self.get_object()
        persist = request.query_params.get("persist", "false").lower() == "true"
        pdf_data = PDFService.generate_estimate_pdf(estimate, persist=persist)
        response = HttpResponse(pdf_data, content_type="application/pdf")
        response["Content-Disposition"] = f'inline; filename="estimate_{estimate.code}.pdf"'
        return response

    @action(detail=True, methods=["post"])
    def persist_pdf(self, request, pk=None):
        estimate = self.get_object()
        PDFService.generate_estimate_pdf(estimate, persist=True)
        estimate.refresh_from_db()
        return Response({
            "detail": "PDF persisted",
            "url": presigned_url_for_file_field(estimate.pdf_file) or None,
        })

@soft_delete_schema_view()
class EstimateServiceViewSet(SoftDeleteViewSetMixin, viewsets.ModelViewSet):
    queryset = EstimateService.all_objects.all()
    serializer_class = EstimateServiceSerializer

    def get_permissions(self):
        if self.action == "hard_delete":
            return [IsTenantUser(), IsAdministrator()]
        return [IsTenantUser(), (IsAdministrator | IsSecretary)()]

    def get_queryset(self):
        require_tenant_access(self.request, write=False)
        qs = EstimateService.all_objects.filter(
            estimate__company_id=resolve_company_id(self.request)
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
        calculate_estimate_totals(instance.estimate)

    def perform_update(self, serializer):
        require_tenant_user(self.request.user)
        instance = serializer.save()
        calculate_estimate_totals(instance.estimate)

    def perform_destroy(self, instance):
        require_tenant_user(self.request.user)
        estimate = instance.estimate
        instance.delete()
        calculate_estimate_totals(estimate)

@soft_delete_schema_view()
class EstimateItemViewSet(SoftDeleteViewSetMixin, viewsets.ModelViewSet):
    queryset = EstimateItem.all_objects.all()
    serializer_class = EstimateItemSerializer

    def get_permissions(self):
        if self.action == "hard_delete":
            return [IsTenantUser(), IsAdministrator()]
        return [IsTenantUser(), (IsAdministrator | IsSecretary)()]

    def get_queryset(self):
        require_tenant_access(self.request, write=False)
        qs = EstimateItem.all_objects.filter(
            estimate__company_id=resolve_company_id(self.request)
        )
        if self.action == "restore":
            return qs.filter(deleted_at__isnull=False)
        if self.action == "hard_delete":
            return qs
        return self.apply_deleted_filter(qs)

    def perform_create(self, serializer):
        require_tenant_user(self.request.user)
        instance = serializer.save()
        calculate_estimate_totals(instance.estimate)

    def perform_update(self, serializer):
        require_tenant_user(self.request.user)
        instance = serializer.save()
        calculate_estimate_totals(instance.estimate)

    def perform_destroy(self, instance):
        require_tenant_user(self.request.user)
        estimate = instance.estimate
        instance.delete()
        calculate_estimate_totals(estimate)
