from uuid import UUID

from celery import shared_task
from celery.utils.log import get_task_logger
from django.db import transaction

from events.models import Issue, RawEvent
from projects.models import Project

from .exceptions import (
    EventAlreadyProcessed,
    InvalidEventData,
    InvalidProjectPublicKey,
)
from .serializers import EventSerializer, RawEventSerializer
from .signatures import calculate_event_signature

logger = get_task_logger(__name__)


@shared_task(ignore_result=True)
def capture_event(project_id, public_key, event_data):
    logger.info("capturing event for project with id '%s'", project_id)

    try:
        project = Project.objects.get(pk=project_id)
    except Project.DoesNotExist as e:
        logger.warning("a project with id '%s' doesn't exist", project_id)
        raise e

    try:
        public_key_uuid = UUID(public_key)
    except ValueError as e:
        logger.warning(
            "the public key given is not a a valid uuid for "
            "project with id '%s'",
            project_id,
        )
        raise InvalidProjectPublicKey() from e

    if project.public_key != public_key_uuid:
        logger.warning(
            "the public key doesn't match the public key of "
            "project with id '%s'",
            project_id,
        )
        raise InvalidProjectPublicKey()

    raw_event_serializer = RawEventSerializer(data=event_data)
    if not raw_event_serializer.is_valid():
        logger.error("received invalid event data")
        raise InvalidEventData()

    logger.info(
        "capturing event with id '%s' for project with id '%s'",
        event_data["event_id"],
        project_id,
    )

    if RawEvent.objects.filter(
        id=raw_event_serializer.validated_data["event_id"]
    ).exists():
        logger.info(
            "an event with id '%s' already exists", event_data["event_id"]
        )
        raise EventAlreadyProcessed()

    raw_event = raw_event_serializer.save(
        project_id=project_id, data=event_data
    )

    event_serializer = EventSerializer(data=raw_event.data)
    if not event_serializer.is_valid():
        logger.error("received invalid event data")
        raise InvalidEventData()

    event = event_serializer.save(
        raw_event=raw_event, project=raw_event.project
    )

    signature = calculate_event_signature(event_data)
    issue = None
    if signature is not None:
        issue = Issue.objects.filter(
            project=project, signature=signature
        ).first()

        if not issue:
            issue = Issue(
                project=project,
                signature=signature,
                primary_event=event,
                first_seen_at=event.timestamp,
                last_seen_at=event.timestamp,
            )

        if event.timestamp < issue.first_seen_at:
            issue.first_seen_at = event.timestamp

        if event.timestamp > issue.last_seen_at:
            issue.last_seen_at = event.timestamp

    event.issue = issue
    with transaction.atomic():
        if issue is not None:
            issue.save()
        raw_event.save()
        event.save()

    logger.info("captured event with id '%s'", event_data["event_id"])

    return str(raw_event.id)
