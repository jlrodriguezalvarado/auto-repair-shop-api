from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

DELETED_QUERY_PARAM = OpenApiParameter(
    name="deleted",
    type=str,
    location=OpenApiParameter.QUERY,
    required=False,
    enum=["false", "true", "all"],
    description="Filter soft-deleted rows. Default false (active only).",
)

def soft_delete_schema_view():
    """Apply OpenAPI list parameter for deleted= on ViewSets using SoftDeleteViewSetMixin."""
    return extend_schema_view(
        list=extend_schema(parameters=[DELETED_QUERY_PARAM]),
    )

class SoftDeleteViewSetMixin:
    """Soft-delete destroy, POST restore, POST hard-delete, and list filter ?deleted=false|true|all."""

    def get_queryset(self):
        qs = super().get_queryset()
        action = getattr(self, "action", None)
        if action == "restore":
            return qs.filter(deleted_at__isnull=False)
        if action == "hard_delete":
            # Include soft-deleted rows; alive rows are rejected with 400 in the action.
            return qs
        return self.apply_deleted_filter(qs)

    def apply_deleted_filter(self, queryset):
        deleted = (self.request.query_params.get("deleted") or "false").strip().lower()
        if deleted == "true":
            return queryset.filter(deleted_at__isnull=False)
        if deleted == "all":
            return queryset
        return queryset.filter(deleted_at__isnull=True)

    def perform_destroy(self, instance):
        instance.delete()

    def perform_hard_delete(self, instance):
        instance.hard_delete()

    @action(detail=True, methods=["post"], url_path="restore")
    def restore(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.restore()
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(request=None, responses={204: None})
    @action(detail=True, methods=["post"], url_path="hard-delete")
    def hard_delete(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.deleted_at is None:
            return Response(
                {"detail": "Only soft-deleted records can be permanently deleted."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        self.perform_hard_delete(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
