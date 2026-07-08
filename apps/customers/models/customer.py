from django.db import models
from django.conf import settings
from apps.common.models import BaseModel
class CustomerProfile(BaseModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="customer_profile")
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    document_id = models.CharField(max_length=50, blank=True, null=True)
    phone = models.CharField(max_length=50)
    secondary_phone = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
