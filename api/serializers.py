from rest_framework import serializers

from events.models import Event


class EventSerializer(serializers.Serializer):
    event_id = serializers.UUIDField(required=True)
    timestamp = serializers.DateTimeField(required=True)
    platform = serializers.CharField(max_length=32, required=True)
    logger = serializers.CharField(required=False, allow_null=True)
    level = serializers.CharField(required=False, allow_null=True)
    transaction = serializers.CharField(required=False, allow_null=True)
    environment = serializers.CharField(required=False, allow_null=True)
    server_name = serializers.CharField(required=False, allow_null=True)

    def _message(self, data):
        if (
            "exception" in data and
            data["exception"] and
            data["exception"]["values"]
        ):
            return data["exception"]["values"][0]["type"]
        elif (
            "logentry" in data and
            data["logentry"] and
            data["logentry"]["message"]
        ):
            return data["logentry"]["message"] % tuple(
                data["logentry"]["params"] or [])
        elif "message" in data and data["message"]:
            return data["message"]

        return f"Event - {data['event_id']}"

    def create(self, validated_data):
        return Event(
            id=validated_data["event_id"],
            timestamp=validated_data["timestamp"],
            platform=validated_data["platform"],
            project_id=validated_data["project_id"],
            message=self._message(validated_data["data"]),
            logger=validated_data.get("logger"),
            level=validated_data.get("level"),
            transaction=validated_data.get("transaction"),
            environment=validated_data.get("environment"),
            server_name=validated_data.get("server_name"),
            data=validated_data["data"]
        )

    def update(self, instance, validated_data):
        raise RuntimeError("it is not allowed to update an event")
