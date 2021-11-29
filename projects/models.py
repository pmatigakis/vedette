from uuid import uuid4

from django.core.validators import MinLengthValidator
from django.db import models


class Project(models.Model):
    name = models.CharField(
        max_length=120,
        null=False,
        blank=False,
        unique=True,
        validators=(MinLengthValidator(limit_value=1),),
    )
    public_key = models.UUIDField(
        default=uuid4, blank=False, null=False, unique=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True, blank=False, null=False
    )
    updated_at = models.DateTimeField(auto_now=True, blank=False, null=False)
