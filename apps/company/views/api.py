from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import viewsets, views, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from drf_spectacular.utils import extend_schema, OpenApiParameter
from apps.company.models import Company
from apps.company.serializers.api import (
    CompanySerializer,
    CompanyCreateSerializer,
)
from apps.company.services import update_user_company
from apps.common.soft_delete import SoftDeleteViewSetMixin, soft_delete_schema_view
from apps.common.tenancy import resolve_company_id, COMPANY_CONTEXT_HEADER
from apps.users.permissions import IsSuperAdmin, IsAdministrator, IsTenantUser

User = get_user_model()

@soft_delete_schema_view()
class CompanyViewSet(SoftDeleteViewSetMixin, viewsets.ModelViewSet):
    """SUPER_ADMIN CRUD for all companies. POST creates company + initial ADMIN."""
    queryset = Company.all_objects.all().order_by("name")
    permission_classes = [IsSuperAdmin]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get_serializer_class(self):
        if self.action == "create":
            return CompanyCreateSerializer
        return CompanySerializer

    def perform_hard_delete(self, instance):
        # User.company is PROTECT; purge tenant users before the company row.
        with transaction.atomic():
            User.all_objects.filter(company_id=instance.pk).hard_delete()
            instance.hard_delete()

class MyCompanyView(views.APIView):
    """Tenant company endpoint. SUPER_ADMIN may GET with X-Company-Id; writes require tenant ADMIN."""
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get_permissions(self):
        if self.request.method == "GET":
            return [IsTenantUser()]
        return [IsTenantUser(), IsAdministrator()]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name=COMPANY_CONTEXT_HEADER,
                type=int,
                location=OpenApiParameter.HEADER,
                required=False,
                description="SUPER_ADMIN read-only company context.",
            ),
        ],
        responses=CompanySerializer,
    )
    def get(self, request):
        company_id = resolve_company_id(request)
        company = Company.objects.filter(pk=company_id).first()
        if not company:
            return Response({"detail": "Company not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(CompanySerializer(company).data)

    @extend_schema(request=CompanySerializer, responses=CompanySerializer)
    def put(self, request):
        company = update_user_company(request.user, request.data, request.FILES.get("logo"))
        if not company:
            return Response({"detail": "Company not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(CompanySerializer(company).data)

    @extend_schema(request=CompanySerializer, responses=CompanySerializer)
    def patch(self, request):
        return self.put(request)
