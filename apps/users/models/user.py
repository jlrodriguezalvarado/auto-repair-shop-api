from django.contrib.auth.models import AbstractUser
from django.db import models
from apps.common.models import BaseModel
class User(AbstractUser, BaseModel):
    class Role(models.TextChoices):
        ADMINISTRATOR = "ADMIN", "Administrator"
        SECRETARY = "SECRETARY", "Secretary"
        MECHANIC = "MECHANIC", "Mechanic"
        CUSTOMER = "CUSTOMER", "Customer"
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.ADMINISTRATOR)
    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
