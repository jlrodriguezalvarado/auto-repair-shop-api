from django.db import models
from apps.common.models import BaseModel
class Company(BaseModel):
    name = models.CharField(max_length=255)
    tax_id = models.CharField(max_length=50)
    address = models.TextField()
    phone = models.CharField(max_length=50)
    secondary_phone = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField()
    logo = models.ImageField(upload_to="company_logos/", blank=True, null=True)
