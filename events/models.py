import json

from django.db import models

from .constants import LOG_LEVELS, SUPPORTED_PLATFORMS


class RawEvent(models.Model):
    id = models.UUIDField(blank=False, null=False, primary_key=True)

    project = models.ForeignKey(
        "projects.Project", blank=False, null=False, on_delete=models.CASCADE
    )

    data = models.JSONField(blank=False, null=False)

    created_at = models.DateTimeField(
        auto_now_add=True, blank=False, null=False
    )

    updated_at = models.DateTimeField(auto_now=True, blank=False, null=False)

    class Meta:
        indexes = [
            models.Index(
                fields=["project_id"], name="ix__raw_event__project_id"
            )
        ]

    def pretty_json_data(self):
        return json.dumps(self.data, indent=4)


class Event(models.Model):
    id = models.UUIDField(blank=False, null=False, primary_key=True)

    project = models.ForeignKey(
        "projects.Project", blank=False, null=False, on_delete=models.CASCADE
    )

    issue = models.ForeignKey(
        "Issue",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="events"
    )

    raw_event = models.OneToOneField(
        "RawEvent",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="event",
    )

    timestamp = models.DateTimeField(null=False, blank=False)

    platform = models.CharField(
        max_length=32,
        choices=tuple(SUPPORTED_PLATFORMS),
        null=False,
        blank=False,
    )

    message = models.TextField(null=False, blank=False)

    logger = models.TextField(null=True, blank=True)

    level = models.CharField(
        choices=LOG_LEVELS, max_length=8, null=True, blank=True
    )

    transaction = models.CharField(max_length=128, null=True, blank=True)

    environment = models.CharField(max_length=256, null=True, blank=True)

    server_name = models.CharField(max_length=256, null=True, blank=True)

    log_message = models.TextField(null=True, blank=True)

    handled = models.BooleanField(blank=False, null=False, default=False)

    mechanism = models.CharField(max_length=32, null=True, blank=True)

    exception_message = models.TextField(null=True, blank=True)

    runtime_name = models.CharField(max_length=64, null=True, blank=True)

    runtime_version = models.CharField(max_length=64, null=True, blank=True)

    runtime_build = models.TextField(null=True, blank=True)

    user = models.TextField(null=True, blank=True)

    resolved = models.BooleanField(blank=False, null=False, default=False)

    created_at = models.DateTimeField(
        auto_now_add=True, blank=False, null=False
    )

    updated_at = models.DateTimeField(auto_now=True, blank=False, null=False)

    resolved_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=["project_id"], name="ix__event__project_id"),
            models.Index(fields=["timestamp"], name="ix__event__timestamp"),
        ]

    # def message(self):
    #     if (
    #         "exception" in self.data and
    #         self.data["exception"] and
    #         self.data["exception"]["values"]
    #     ):
    #         return self.data["exception"]["values"][0]["type"]
    #     elif (
    #         "logentry" in self.data and
    #         self.data["logentry"] and
    #         self.data["logentry"]["message"]
    #     ):
    #         return self.data["logentry"]["message"] % tuple(
    #             self.data["logentry"]["params"] or [])
    #     elif "message" in self.data and self.data["message"]:
    #         return self.data["message"]
    #
    #     return f"Event - {self.id}"

    # def logger(self):
    #     return self.data.get("logger")

    # def level(self):
    #     return self.data.get("level")

    # def transaction(self):
    #     return self.data.get("transaction")

    # def exception_message(self):
    #     if (
    #         "exception" in self.data and
    #         self.data["exception"] and
    #         self.data["exception"]["values"]
    #     ):
    #         return self.data["exception"]["values"][0]["value"]

    # def user_tag_value(self):
    #     user_data = self.raw_event.data.get("user", {})
    #     return (
    #             user_data.get("id") or
    #             user_data.get("username") or
    #             user_data.get("email") or
    #             user_data.get("ip_address")
    #     )

    # def runtime_tag_value(self):
    #     runtime = self.data.get("contexts", {}).get("runtime", {})
    #
    #     components = []
    #     if "name" in runtime:
    #         components.append(runtime["name"])
    #     if "version" in runtime:
    #         components.append(runtime["version"])
    #
    #     runtime_tag = "-".join(components)
    #     if not runtime_tag:
    #         runtime_tag = None
    #
    #     return runtime_tag

    def runtime_tag_value(self):
        components = []
        if self.runtime_name:
            components.append(self.runtime_name)
        if self.runtime_version:
            components.append(self.runtime_version)

        runtime_tag = "-".join(components)
        if not runtime_tag:
            runtime_tag = None

        return runtime_tag

    def user_defined_tags(self):
        return self.raw_event.data.get("tags", {})

    # def environment(self):
    #     return self.data.get("environment")

    # def handled(self):
    #     exceptions = self.data.get("exception", {}).get("values")
    #     if exceptions and exceptions[0]["mechanism"]:
    #         return exceptions[0]["mechanism"].get("handled") or False
    #
    #     return False

    # def mechanism(self):
    #     if "exception" in self.data:
    #         exception_values = self.data["exception"].get("values", [])
    #         if exception_values:
    #             return exception_values[0].get("mechanism", {}).get("type")
    #     elif "logentry" in self.data:
    #         return "logging"
    #
    #     return None

    # def runtime_name(self):
    #     return self.data.get("contexts", {}).get("runtime", {}).get("name")

    # def server_name(self):
    #     return self.data.get("server_name")

    # def log_message(self):
    #     message = self.data.get("logentry", {}).get("message")
    #     if message:
    #         return message % tuple(
    #         self.data.get("logentry", {}).get("params", []))
    #
    #     return None

    def log_params(self):
        return self.raw_event.data.get("logentry", {}).get("params", [])


class Issue(models.Model):
    project = models.ForeignKey(
        "projects.Project", blank=False, null=False, on_delete=models.CASCADE
    )
    signature = models.CharField(max_length=64, blank=False, null=False)
    primary_event = models.ForeignKey(
        "Event",
        blank=False,
        null=False,
        on_delete=models.CASCADE,
        related_name="primary_issues"
    )
    resolved = models.BooleanField(blank=False, null=False, default=False)
    created_at = models.DateTimeField(
        auto_now_add=True,
        blank=False,
        null=False
    )
    updated_at = models.DateTimeField(auto_now=True, blank=False, null=False)
    resolved_at = models.DateTimeField(blank=True, null=True)
    first_seen_at = models.DateTimeField(blank=False, null=False)
    last_seen_at = models.DateTimeField(blank=False, null=False)

    class Meta:
        unique_together = ["project_id", "signature"]
        indexes = [
            models.Index(fields=["project_id"], name="ix__issue__project_id")
        ]
