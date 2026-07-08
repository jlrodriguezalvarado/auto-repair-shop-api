from rest_framework import serializers
from apps.catalog.models import ServiceCatalog

class ServiceCatalogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceCatalog
        fields = "__all__"
