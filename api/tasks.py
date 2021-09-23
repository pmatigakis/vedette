from uuid import UUID
import json
import zlib
import base64
from urllib.parse import urlparse

from celery import shared_task
from celery.utils.log import get_task_logger
import requests

from events.models import RawEvent
from projects.models import Project
from .serializers import RawEventSerializer, EventSerializer
from .exceptions import (
    InvalidProjectPublicKey, InvalidEventData, EventAlreadyProcessed,
    InvalidSentryDsn
)


logger = get_task_logger(__name__)


@shared_task
def capture_event(project_id, public_key, event_data):
    logger.info("capturing event with id '%s'", event_data["event_id"])

    try:
        project = Project.objects.get(pk=project_id)
    except Project.DoesNotExist as e:
        logger.warning("a project with id '%s' doesn't exist", project_id)
        raise e

    if project.public_key != UUID(public_key):
        logger.warning("the public key doesn't match the public key of "
                       "project with id '%s'", project_id)
        raise InvalidProjectPublicKey()

    serializer = RawEventSerializer(data=event_data)
    if not serializer.is_valid():
        logger.error("received invalid event data")
        raise InvalidEventData()

    if RawEvent.objects.filter(
            id=serializer.validated_data["event_id"]).exists():
        logger.info(
            "an event with id '%s' already exists", event_data["event_id"])
        raise EventAlreadyProcessed()

    raw_event = serializer.save(
        project_id=project_id,
        data=event_data
    )
    raw_event.save()

    logger.info("captured event with id '%s'", event_data["event_id"])

    return str(raw_event.id)


@shared_task(ignore_result=True)
def process_event(event_id):
    logger.info("processing event with id '%s'", event_id)

    try:
        raw_event = RawEvent.objects.get(pk=UUID(event_id))
    except RawEvent.DoesNotExist as e:
        logger.warning("a raw event with id '%s' doesn't exist", event_id)
        raise e

    if hasattr(raw_event, "event"):
        logger.warning("an event with id '%s' already exists", event_id)
        raise EventAlreadyProcessed()

    serializer = EventSerializer(data=raw_event.data)
    if not serializer.is_valid():
        logger.error("received invalid event data")
        raise InvalidEventData()

    event = serializer.save(raw_event=raw_event, project=raw_event.project)
    event.save()

    logger.info("processed event with id '%s'", event_id)


@shared_task(ignore_result=True)
def forward_to_sentry(project_id, event_data):
    logger.info(
        "forwarding event with id '%s' to sentry", event_data["event_id"]
    )

    try:
        project = Project.objects.get(pk=project_id)
    except Project.DoesNotExist as e:
        logger.warning("a project with id '%s' doesn't exist", project_id)
        raise e

    if project.sentry_dsn is None:
        logger.info(
            "not forwarding event because the project with id '%s' doesn't "
            "have a sentry DSN", project_id
        )
        return

    serializer = RawEventSerializer(data=event_data)
    if not serializer.is_valid():
        logger.error("received invalid event data")
        raise InvalidEventData()

    parsed_dsn = urlparse(project.sentry_dsn)
    if not all([parsed_dsn.scheme, parsed_dsn.netloc, parsed_dsn.path]):
        logger.error("invalid sentry dsn %s", project.sentry_dsn)
        raise InvalidSentryDsn()

    try:
        public_key, host = parsed_dsn.netloc.split("@")
    except ValueError:
        logger.error("invalid sentry dsn %s", project.sentry_dsn)
        raise InvalidSentryDsn()

    project_id = parsed_dsn.path[1:]
    if not project_id:
        logger.error("invalid project id in sentry dsn %s", project.sentry_dsn)
        raise InvalidSentryDsn()

    url = f"{parsed_dsn.scheme}://{public_key}@{host}/api/{project_id}/store/"
    compressed_payload = base64.b64encode(
        zlib.compress(json.dumps(event_data).encode())
    )
    headers = {
        "Content-Type": "application/json",
        "Content-Encoding": None,
        "User-Agent": "vedette/0.1.0",
        "X-Sentry-Auth": f"Sentry sentry_key={public_key}, "
                         f"sentry_version=7, sentry_client=vedette/0.1.0"

    }

    response = requests.post(
        url,
        data=compressed_payload,
        headers=headers,
        timeout=5
    )

    logger.info(
        "Event for project %s with id %s submission status code is %s",
        project_id, event_data["event_id"], response.status_code
    )
