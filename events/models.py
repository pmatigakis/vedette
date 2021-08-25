import json

from django.db import models


SUPPORTED_PLATFORMS = (
    ("python", "Python"),
)


class Event(models.Model):
    id = models.UUIDField(
        blank=False,
        null=False,
        primary_key=True
    )

    project = models.ForeignKey(
        "projects.Project",
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

    def pretty_json_data(self):
        return json.dumps(self.data, indent=4)

    def message(self):
        if (
                "logentry" in self.data and
                self.data["logentry"] and
                self.data["logentry"]["message"]
        ):
            return self.data["logentry"]["message"] % tuple(
                self.data["logentry"]["params"])
        elif (
                "exception" in self.data and
                self.data["exception"] and
                self.data["exception"]["values"]
        ):
            return (
                f'{self.data["exception"]["values"][0]["type"]} - '
                f'{self.data["exception"]["values"][0]["value"]}'
            )
        elif "message" in self.data and self.data["message"]:
            return self.data["message"]

        return f"Event - {self.id}"
