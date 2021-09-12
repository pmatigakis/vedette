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
            "exception" in self.data and
            self.data["exception"] and
            self.data["exception"]["values"]
        ):
            return self.data["exception"]["values"][0]["type"]
        elif (
            "logentry" in self.data and
            self.data["logentry"] and
            self.data["logentry"]["message"]
        ):
            return self.data["logentry"]["message"] % tuple(
                self.data["logentry"]["params"] or [])
        elif "message" in self.data and self.data["message"]:
            return self.data["message"]

        return f"Event - {self.id}"

    def logger(self):
        return self.data.get("logger")

    def level(self):
        return self.data.get("level")

    def transaction(self):
        return self.data.get("transaction")

    def exception_message(self):
        if (
            "exception" in self.data and
            self.data["exception"] and
            self.data["exception"]["values"]
        ):
            return self.data["exception"]["values"][0]["value"]

    def user_tag_value(self):
        user_data = self.data.get("user", {})
        return (
                user_data.get("id") or
                user_data.get("username") or
                user_data.get("email") or
                user_data.get("ip_address")
        )

    def runtime_tag_value(self):
        runtime = self.data.get("contexts", {}).get("runtime", {})

        components = []
        if "name" in runtime:
            components.append(runtime["name"])
        if "version" in runtime:
            components.append(runtime["version"])

        runtime_tag = "-".join(components)
        if not  runtime_tag:
            runtime_tag = None

        return runtime_tag

    def user_defined_tags(self):
        return self.data.get("tags", {})

    def environment(self):
        return self.data.get("environment")

    def handled(self):
        exceptions = self.data.get("exception", {}).get("values")
        if exceptions and exceptions[0]["mechanism"]:
            return exceptions[0]["mechanism"].get("handled") or False

        return False

    def mechanism(self):
        if "exception" in self.data:
            exception_values = self.data["exception"].get("values", [])
            if exception_values:
                return exception_values[0].get("mechanism", {}).get("type")
        elif "logentry" in self.data:
            return "logging"

        return None

    def runtime_name(self):
        return self.data.get("contexts", {}).get("runtime", {}).get("name")

    def server_name(self):
        return self.data.get("server_name")

    def log_message(self):
        message = self.data.get("logentry", {}).get("message")
        if message:
            return message % tuple(self.data.get("logentry", {}).get("params", []))

        return None

    def log_params(self):
        return self.data.get("logentry", {}).get("params", [])
