from rest_framework import serializers

from events.models import Event, RawEvent


class RawEventSerializer(serializers.Serializer):
    event_id = serializers.UUIDField(required=True)
    timestamp = serializers.DateTimeField(required=True)
    platform = serializers.CharField(max_length=32, required=True)

    def create(self, validated_data):
        return RawEvent(
            id=validated_data["event_id"],
            project_id=validated_data["project_id"],
            data=validated_data["data"],
        )

    def update(self, instance, validated_data):
        raise RuntimeError("it is not allowed to update a raw event")


class LogentrySerializer(serializers.Serializer):
    message = serializers.CharField(required=True)
    # this param is an array but we will parse it as json
    params = serializers.JSONField(required=False)


class EventSerializer(serializers.Serializer):
    event_id = serializers.UUIDField(required=True)
    timestamp = serializers.DateTimeField(required=True)
    platform = serializers.CharField(max_length=32, required=True)
    logger = serializers.CharField(required=False, allow_null=True)
    level = serializers.CharField(required=False, allow_null=True)
    transaction = serializers.CharField(required=False, allow_null=True)
    environment = serializers.CharField(required=False, allow_null=True)
    server_name = serializers.CharField(required=False, allow_null=True)
    logentry = LogentrySerializer(required=False)

    def _message(self, data):
        if (
            "exception" in data
            and data["exception"]
            and data["exception"]["values"]
        ):
            return data["exception"]["values"][0]["type"]
        elif (
            "logentry" in data
            and data["logentry"]
            and data["logentry"]["message"]
        ):
            return data["logentry"]["message"] % tuple(
                data["logentry"]["params"] or []
            )
        elif "message" in data and data["message"]:
            return data["message"]

        return f"Event - {data['event_id']}"

    def _log_message(self, logentry):
        if not logentry:
            return None

        message = logentry["message"]
        if message:
            return message % tuple(logentry.get("params", []))

        return None

    def _handled(self, data):
        exceptions = data.get("exception", {}).get("values")
        if exceptions and exceptions[0]["mechanism"]:
            return exceptions[0]["mechanism"].get("handled") or False

        return False

    def _mechanism(self, data):
        if "exception" in data:
            exception_values = data["exception"].get("values", [])
            if exception_values:
                return exception_values[0].get("mechanism", {}).get("type")
        elif "logentry" in data:
            return "logging"

        return None

    def _exception_message(self, data):
        if (
            "exception" in data
            and data["exception"]
            and data["exception"]["values"]
        ):
            message = data["exception"]["values"][0]["value"]
            if not isinstance(message, str):
                message = str(message)

            return message

        return None

    def _runtime_name(self, data):
        return data.get("contexts", {}).get("runtime", {}).get("name")

    def _runtime_version(self, data):
        return data.get("contexts", {}).get("runtime", {}).get("version")

    def _runtime_build(self, data):
        return data.get("contexts", {}).get("runtime", {}).get("build")

    def _user(self, data):
        user_data = data.get("user", {})

        return (
            user_data.get("id")
            or user_data.get("username")
            or user_data.get("email")
            or user_data.get("ip_address")
        )

    def create(self, validated_data):
        return Event(
            id=validated_data["event_id"],
            project=validated_data["project"],
            raw_event_id=validated_data["raw_event"].id,
            timestamp=validated_data["timestamp"],
            platform=validated_data["platform"],
            message=self._message(validated_data["raw_event"].data),
            logger=validated_data.get("logger"),
            level=validated_data.get("level"),
            transaction=validated_data.get("transaction"),
            environment=validated_data.get("environment"),
            server_name=validated_data.get("server_name"),
            log_message=self._log_message(validated_data.get("logentry")),
            handled=self._handled(validated_data["raw_event"].data),
            mechanism=self._mechanism(validated_data["raw_event"].data),
            exception_message=self._exception_message(
                validated_data["raw_event"].data
            ),
            runtime_name=self._runtime_name(validated_data["raw_event"].data),
            runtime_version=self._runtime_version(
                validated_data["raw_event"].data
            ),
            runtime_build=self._runtime_build(
                validated_data["raw_event"].data
            ),
            user=self._user(validated_data["raw_event"].data),
        )

    def update(self, instance, validated_data):
        raise RuntimeError("it is not allowed to update an event")
