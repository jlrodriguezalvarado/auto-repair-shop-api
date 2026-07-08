from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import HttpResponse
from apps.estimates.models import Estimate, EstimateService, EstimateItem
from apps.estimates.serializers.api import EstimateSerializer, EstimateServiceSerializer, EstimateItemSerializer
from apps.estimates.services import calculate_estimate_totals, create_work_order_from_estimate
from apps.common.services.pdf_service import PDFService
from apps.users.permissions import IsAdministrator, IsSecretary, IsCustomer

class EstimateViewSet(viewsets.ModelViewSet):
    queryset = Estimate.objects.all().prefetch_related("services", "items")
    serializer_class = EstimateSerializer

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
    def approve(self, request, pk=None):
        estimate = self.get_object()
        estimate.status = Estimate.Status.APPROVED
        estimate.save()
        calculate_estimate_totals(estimate)
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
        return Response({"detail": "PDF persisted", "url": estimate.pdf_file.url if estimate.pdf_file else None})


class EstimateServiceViewSet(viewsets.ModelViewSet):
    queryset = EstimateService.objects.all()
    serializer_class = EstimateServiceSerializer
    permission_classes = [IsAdministrator | IsSecretary]

    def perform_create(self, serializer):
        service = serializer.validated_data['service']
        instance = serializer.save(
            name_snapshot=service.name,
            description_snapshot=service.description,
            unit_price=serializer.validated_data.get('unit_price', service.base_price)
        )
        calculate_estimate_totals(instance.estimate)

    def perform_update(self, serializer):
        instance = serializer.save()
        calculate_estimate_totals(instance.estimate)

    def perform_destroy(self, instance):
        estimate = instance.estimate
        instance.delete()
        calculate_estimate_totals(estimate)


class EstimateItemViewSet(viewsets.ModelViewSet):
    queryset = EstimateItem.objects.all()
    serializer_class = EstimateItemSerializer
    permission_classes = [IsAdministrator | IsSecretary]

    def perform_create(self, serializer):
        instance = serializer.save()
        calculate_estimate_totals(instance.estimate)

    def perform_update(self, serializer):
        instance = serializer.save()
        calculate_estimate_totals(instance.estimate)

    def perform_destroy(self, instance):
        estimate = instance.estimate
        instance.delete()
        calculate_estimate_totals(estimate)
