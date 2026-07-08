from rest_framework import views, status, permissions
from rest_framework.response import Response
from apps.company.serializers.api import CompanySerializer
from apps.company.services import get_company, update_company
from apps.users.permissions import IsAdministrator

class CompanyView(views.APIView):
    def get_permissions(self):
        if self.request.method == "GET":
            return [permissions.IsAuthenticated()]
        return [IsAdministrator()]

    def get(self, request):
        company = get_company()
        if not company:
            return Response({"detail": "Company not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = CompanySerializer(company)
        return Response(serializer.data)

    def put(self, request):
        company = update_company(request.data, request.FILES.get("logo"))
        serializer = CompanySerializer(company)
        return Response(serializer.data)

    def patch(self, request):
        return self.put(request)
