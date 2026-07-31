from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import SAFE_METHODS

SUPER_ADMIN_ROLE = "SUPER_ADMIN"
# SUPER_ADMIN read-only company context on SAFE methods (see resolve_company_id / permissions).
COMPANY_CONTEXT_HEADER = "X-Company-Id"

def is_super_admin(user) -> bool:
    return bool(user and user.is_authenticated and getattr(user, "role", None) == SUPER_ADMIN_ROLE)

def require_tenant_user(user):
    """Raise 403 if the user is SUPER_ADMIN or has no company."""
    if not user or not user.is_authenticated:
        raise PermissionDenied("Authentication required.")
    if is_super_admin(user):
        raise PermissionDenied("Super admins cannot access tenant business endpoints.")
    if not getattr(user, "company_id", None):
        raise PermissionDenied("User is not assigned to a company.")
    return user

def parse_company_context_id(request) -> int | None:
    """Read X-Company-Id. Missing → None; invalid format → PermissionDenied."""
    raw = request.headers.get(COMPANY_CONTEXT_HEADER)
    if raw is None or raw == "":
        return None
    try:
        return int(raw)
    except (TypeError, ValueError):
        raise PermissionDenied("Invalid X-Company-Id header.")

def company_exists(company_id: int) -> bool:
    """True only for non-soft-deleted companies (Company.objects excludes deleted)."""
    from apps.company.models import Company
    return Company.objects.filter(pk=company_id).exists()

def resolve_company_id(request) -> int:
    """Tenant users: their company_id. SUPER_ADMIN: valid X-Company-Id of an existing company."""
    user = request.user
    if not user or not user.is_authenticated:
        raise PermissionDenied("Authentication required.")
    if is_super_admin(user):
        company_id = parse_company_context_id(request)
        if company_id is None:
            raise PermissionDenied("Super admins require X-Company-Id for tenant reads.")
        if not company_exists(company_id):
            raise PermissionDenied("Company not found.")
        return company_id
    if not getattr(user, "company_id", None):
        raise PermissionDenied("User is not assigned to a company.")
    return user.company_id

def require_tenant_access(request, *, write: bool = False):
    """Write: real tenant only. Read: tenant or SUPER_ADMIN with resolvable company header."""
    if write:
        return require_tenant_user(request.user)
    resolve_company_id(request)
    return request.user

def is_super_admin_company_viewer(request) -> bool:
    """True when SUPER_ADMIN on SAFE method with present, parseable, existing company header."""
    user = request.user
    if not user or not user.is_authenticated or not is_super_admin(user):
        return False
    if request.method not in SAFE_METHODS:
        return False
    try:
        company_id = parse_company_context_id(request)
    except PermissionDenied:
        return False
    if company_id is None:
        return False
    return company_exists(company_id)

class TenantQuerysetMixin:
    """Scope querysets by resolved company. SUPER_ADMIN may read with X-Company-Id; writes deny SUPER_ADMIN.
    ViewSet querysets must use Model.all_objects so SoftDeleteViewSetMixin can apply ?deleted=.
    """
    company_lookup = "company_id"

    def get_queryset(self):
        require_tenant_access(self.request, write=False)
        company_id = resolve_company_id(self.request)
        qs = super().get_queryset()
        return qs.filter(**{self.company_lookup: company_id})

    def perform_create(self, serializer):
        require_tenant_user(self.request.user)
        serializer.save(company_id=self.request.user.company_id)
