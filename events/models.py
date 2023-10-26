import json
from datetime import datetime, timezone
from uuid import uuid4

from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVector
from django.core.validators import MinLengthValidator
from django.db import models

from .constants import LOG_LEVELS, SUPPORTED_PLATFORMS
from .managers import EventManager, IssueManager


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


class RawEvent(models.Model):
    id = models.UUIDField(blank=False, null=False, primary_key=True)
    project = models.ForeignKey(
        "Project", blank=False, null=False, on_delete=models.CASCADE
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
    objects = EventManager()
    id = models.UUIDField(blank=False, null=False, primary_key=True)
    project = models.ForeignKey(
        "Project", blank=False, null=False, on_delete=models.CASCADE
    )
    issue = models.ForeignKey(
        "Issue",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="events",
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
            GinIndex(
                SearchVector(
                    "message",
                    "log_message",
                    "exception_message",
                    config="english",
                ),
                name="events_search_vector_idx",
            ),
        ]

    def resolve(self):
        self.resolved = True
        self.resolved_at = datetime.utcnow().replace(tzinfo=timezone.utc)

    def unresolve(self):
        self.resolved = False
        self.resolved_at = None

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

    def log_params(self):
        return self.raw_event.data.get("logentry", {}).get("params", [])

    def _timestamp_string_to_datetime(self, timestamp):
        if not timestamp:
            return None

        return datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")

    def _pretty_json_data(self, data):
        if not data:
            return None

        return json.dumps(data, indent=4)

    def breadcrumbs(self):
        return [
            {
                "type": breadcrumb.get("type"),
                "category": breadcrumb.get("category"),
                "message": breadcrumb.get("message"),
                "level": breadcrumb.get("level"),
                "time": self._timestamp_string_to_datetime(
                    breadcrumb.get("timestamp")
                ),
                "data": self._pretty_json_data(breadcrumb.get("data")),
            }
            for breadcrumb in self.raw_event.data.get("breadcrumbs", {}).get(
                "values", []
            )
        ]

    def _create_code_snippet(self, stacktrace):
        code = []
        code.extend(stacktrace.get("pre_context", []))
        if "context_line" in stacktrace:
            code.append(stacktrace["context_line"])
        code.extend(stacktrace.get("post_context", []))

        if "lineno" in stacktrace:
            offset = stacktrace["lineno"] - len(
                stacktrace.get("pre_context", [])
            )
            code = [
                f"{index + offset}) {line}" for index, line in enumerate(code)
            ]

        return "\n".join(code)

    def stacktraces(self):
        values = self.raw_event.data.get("exception", {}).get("values", [])
        if not values:
            return []

        return [
            {
                "vars": _stacktrace.get("vars", {}),
                "lineno": _stacktrace.get("lineno"),
                "module": _stacktrace.get("module"),
                "code": self._create_code_snippet(_stacktrace),
            }
            for _stacktrace in (
                values[0].get("stacktrace", {}).get("frames", [])
            )
        ]


class Issue(models.Model):
    objects = IssueManager()
    project = models.ForeignKey(
        "Project", blank=False, null=False, on_delete=models.CASCADE
    )
    signature = models.CharField(max_length=64, blank=False, null=False)
    primary_event = models.ForeignKey(
        "Event",
        blank=False,
        null=False,
        on_delete=models.CASCADE,
        related_name="primary_issues",
    )
    resolved = models.BooleanField(blank=False, null=False, default=False)
    created_at = models.DateTimeField(
        auto_now_add=True, blank=False, null=False
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

    def resolve(self):
        self.resolved = True
        self.resolved_at = datetime.utcnow().replace(tzinfo=timezone.utc)

    def unresolve(self):
        self.resolved = False
        self.resolved_at = None
