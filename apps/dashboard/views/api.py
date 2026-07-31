from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter
from apps.dashboard.selectors import DashboardSelectors
from apps.users.permissions import IsAdministrator, IsSecretary, IsTenantUser
from apps.common.tenancy import require_tenant_access, resolve_company_id, COMPANY_CONTEXT_HEADER

class DashboardSummaryView(APIView):
    permission_classes = [IsTenantUser, IsAdministrator | IsSecretary]

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
        responses={200: dict},
    )
    def get(self, request):
        require_tenant_access(request, write=False)
        period = request.query_params.get("period")
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")
        summary = DashboardSelectors.get_summary(
            company_id=resolve_company_id(request),
            start_date=start_date,
            end_date=end_date,
            period=period,
        )
        return Response(summary)
