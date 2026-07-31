from rest_framework import permissions
from apps.common.tenancy import SUPER_ADMIN_ROLE, is_super_admin_company_viewer

class IsSuperAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == SUPER_ADMIN_ROLE
        )

class IsTenantUser(permissions.BasePermission):
    """Authenticated tenant staff/customer, or SUPER_ADMIN read-only company viewer."""
    def has_permission(self, request, view):
        user = request.user
        if is_super_admin_company_viewer(request):
            return True
        return (
            user.is_authenticated
            and user.role != SUPER_ADMIN_ROLE
            and user.company_id is not None
        )

class IsAdministrator(permissions.BasePermission):
    def has_permission(self, request, view):
        if is_super_admin_company_viewer(request):
            return True
        return request.user.is_authenticated and request.user.role == "ADMIN"

class IsSecretary(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "SECRETARY"

class IsMechanic(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "MECHANIC"

class IsCustomer(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "CUSTOMER"
