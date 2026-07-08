from django.db import models
from apps.common.models import BaseModel
class ServiceCatalog(BaseModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    base_price = models.DecimalField(max_digits=12, decimal_places=2)
    estimated_duration_minutes = models.IntegerField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
