from rest_framework import viewsets, permissions
<<<<<<< HEAD
from rest_framework.decorators import action
=======
from rest_framework.views import APIView
>>>>>>> 57e364fbf09a38203cf48b12a33136d53157d211
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from apps.common.soft_delete import SoftDeleteViewSetMixin, soft_delete_schema_view
from apps.common.tenancy import TenantQuerysetMixin, require_tenant_user, require_tenant_access, resolve_company_id
from apps.users.serializers.api import UserSerializer, UserCreateSerializer
from apps.users.permissions import IsTenantUser, IsAdministrator

User = get_user_model()

<<<<<<< HEAD
@soft_delete_schema_view()
class UserViewSet(SoftDeleteViewSetMixin, TenantQuerysetMixin, viewsets.ModelViewSet):
    queryset = User.all_objects.select_related("company").all()
=======
class CurrentUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        return Response(UserSerializer(request.user).data)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
>>>>>>> 57e364fbf09a38203cf48b12a33136d53157d211

    def get_serializer_class(self):
        if self.action == "create":
            return UserCreateSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action == "me":
            return [permissions.IsAuthenticated()]
        if self.action in ["create", "update", "partial_update", "destroy", "restore", "hard_delete"]:
            return [IsTenantUser(), IsAdministrator()]
        return [IsTenantUser()]

    def get_queryset(self):
        if self.action == "me":
            return User.all_objects.select_related("company").filter(pk=self.request.user.pk)
        require_tenant_access(self.request, write=False)
        qs = User.all_objects.select_related("company").filter(
            company_id=resolve_company_id(self.request)
        )
        if self.action == "restore":
            return qs.filter(deleted_at__isnull=False)
        if self.action == "hard_delete":
            return qs
        return self.apply_deleted_filter(qs)

    def perform_create(self, serializer):
        require_tenant_user(self.request.user)
        serializer.save()

    @action(detail=False, methods=["get"], url_path="me")
    def me(self, request):
        return Response(UserSerializer(request.user).data)
