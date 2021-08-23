from uuid import uuid4

from django.db import models
from django.core.validators import MinLengthValidator


SUPPORTED_PLATFORMS = (
    ("python", "Python"),
)


class Project(models.Model):
    title = models.CharField(
        max_length=120,
        null=False,
        blank=False,
        unique=True,
        validators=(MinLengthValidator(limit_value=1),)
    )

    public_key = models.UUIDField(
        default=uuid4,
        blank=False,
        null=False,
        unique=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        blank=False,
        null=False
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        blank=False,
        null=False
    )


class Event(models.Model):
    id = models.UUIDField(
        blank=False,
        null=False,
        primary_key=True
    )

    project = models.ForeignKey(
        "Project",
        blank=False,
        null=False,
        on_delete=models.CASCADE
    )

    timestamp = models.DateTimeField(null=False, blank=False)

    platform = models.CharField(
        max_length=32,
        choices=tuple(SUPPORTED_PLATFORMS),
        null=False,
        blank=False
    )

    data = models.JSONField(blank=False, null=False)

    created_at = models.DateTimeField(
        auto_now_add=True,
        blank=False,
        null=False
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        blank=False,
        null=False
    )

    class Meta:
        indexes = [
            models.Index(
                fields=["project_id"],
                name="ix__event__project_id__project"
            ),
            models.Index(
                fields=["timestamp"],
                name="ix__event__timestamp"
            )
        ]
