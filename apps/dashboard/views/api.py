from rest_framework.views import APIView
from rest_framework.response import Response
from apps.dashboard.selectors import DashboardSelectors
from apps.users.permissions import IsAdministrator, IsSecretary

class DashboardSummaryView(APIView):
    permission_classes = [IsAdministrator | IsSecretary]

    def get(self, request):
        period = request.query_params.get("period")
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")

        summary = DashboardSelectors.get_summary(
            start_date=start_date,
            end_date=end_date,
            period=period
        )
        return Response(summary)
