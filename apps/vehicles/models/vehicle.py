from django.db import models
from apps.common.models import BaseModel
from apps.customers.models import CustomerProfile
class Vehicle(BaseModel):
    customer = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE, related_name="vehicles")
    plate = models.CharField(max_length=20, unique=True)
    brand = models.CharField(max_length=100, blank=True, null=True)
    model = models.CharField(max_length=100, blank=True, null=True)
    year = models.IntegerField(blank=True, null=True)
    color = models.CharField(max_length=50, blank=True, null=True)
    photo = models.ImageField(upload_to="vehicle_photos/", blank=True, null=True)
    vin = models.CharField(max_length=50, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
