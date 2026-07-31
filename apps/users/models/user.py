from django.contrib.auth.models import AbstractUser, UserManager
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError
from django.db import models
from apps.common.models.base import BaseModel, SoftDeleteQuerySet

class SoftDeleteUserManager(UserManager.from_queryset(SoftDeleteQuerySet)):
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)

class SoftDeleteUserAllManager(UserManager.from_queryset(SoftDeleteQuerySet)):
    pass

class User(AbstractUser, BaseModel):
    class Role(models.TextChoices):
        SUPER_ADMIN = "SUPER_ADMIN", "Super Admin"
        ADMINISTRATOR = "ADMIN", "Administrator"
        SECRETARY = "SECRETARY", "Secretary"
        MECHANIC = "MECHANIC", "Mechanic"
        CUSTOMER = "CUSTOMER", "Customer"
    username_validator = UnicodeUsernameValidator()
    # Drop AbstractUser unique=True; enforce uniqueness only among non-deleted rows.
    username = models.CharField(
        "username",
        max_length=150,
        unique=False,
        help_text="Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.",
        validators=[username_validator],
        error_messages={"unique": "A user with that username already exists."},
    )
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.ADMINISTRATOR)
    company = models.ForeignKey(
        "company.Company",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="users",
    )
    tokens_invalid_before = models.DateTimeField(null=True, blank=True)
    objects = SoftDeleteUserManager()
    all_objects = SoftDeleteUserAllManager()

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ["id"]
        constraints = [
            models.UniqueConstraint(
                fields=["username"],
                condition=models.Q(deleted_at__isnull=True),
                name="uniq_user_username_alive",
            ),
        ]

    def clean(self):
        super().clean()
        if self.role == self.Role.SUPER_ADMIN and self.company_id is not None:
            raise ValidationError({"company": "SUPER_ADMIN must not belong to a company."})
        if self.role != self.Role.SUPER_ADMIN and self.company_id is None:
            raise ValidationError({"company": "Tenant users must belong to a company."})
