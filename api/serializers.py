from rest_framework import serializers

from events.models import Event


class EventSerializer(serializers.Serializer):
    event_id = serializers.UUIDField(required=True)
    timestamp = serializers.DateTimeField(required=True)
    platform = serializers.CharField(max_length=32, required=True)

    def create(self, validated_data):
        return Event(
            id=validated_data["event_id"],
            timestamp=validated_data["timestamp"],
            platform=validated_data["platform"],
            project_id=validated_data["project_id"],
            data=validated_data["data"]
        )

    def update(self, instance, validated_data):
        raise RuntimeError("it is not allowed to update an event")
