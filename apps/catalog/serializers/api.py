from rest_framework import serializers
from apps.catalog.models import ServiceCatalog

class ServiceCatalogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceCatalog
        fields = "__all__"
        read_only_fields = ("company", "deleted_at")
