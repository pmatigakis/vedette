from uuid import UUID

from celery import shared_task
from celery.utils.log import get_task_logger

from events.models import Event
from projects.models import Project
from .serializers import EventSerializer


logger = get_task_logger(__name__)


@shared_task(ignore_result=True)
def capture_event(project_id, public_key, event_data):
    logger.info("processing event with id '%s'", event_data["event_id"])

    try:
        project = Project.objects.get(pk=project_id)
    except Project.DoesNotExist:
        logger.warning("a project with id '%s' doesn't exist", project_id)
        return

    if project.public_key != UUID(public_key):
        logger.warning("the public key doesn't match the public key of "
                       "project with id '%s'", project_id)
        return

    serializer = EventSerializer(data=event_data)
    if not serializer.is_valid():
        logger.error("received invalid event data")
        return

    if Event.objects.filter(
            id=serializer.validated_data["event_id"]).exists():
        logger.info(
            "an event with id '%s' already exists", event_data["event_id"])
        return

    event = serializer.save(
        project_id=project_id,
        data=event_data
    )
    event.save()

    logger.info("processed event with id '%s'", event_data["event_id"])
