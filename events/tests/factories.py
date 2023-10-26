from datetime import datetime, timezone
from uuid import uuid4

import factory

from events.models import Event, Issue, Project, RawEvent


class ProjectFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Project

    name = factory.Sequence(lambda n: f"project-{n}")
    public_key = factory.LazyFunction(lambda: uuid4())
    created_at = factory.LazyFunction(
        lambda: datetime.utcnow().replace(tzinfo=timezone.utc)
    )
    updated_at = factory.LazyAttribute(lambda obj: obj.created_at)


class RawEventFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = RawEvent

    id = factory.LazyFunction(lambda: uuid4())
    project = factory.SubFactory(ProjectFactory)
    data = factory.LazyFunction(lambda: {})
    created_at = factory.LazyFunction(
        lambda: datetime.utcnow().replace(tzinfo=timezone.utc)
    )
    updated_at = factory.LazyAttribute(lambda obj: obj.created_at)


class EventIssueFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Issue

    signature = "signature"
    project = None
    resolved = False
    resolved_at = None
    primary_event_id = None
    created_at = factory.LazyFunction(
        lambda: datetime.utcnow().replace(tzinfo=timezone.utc)
    )
    updated_at = factory.LazyAttribute(lambda obj: obj.created_at)
    first_seen_at = factory.LazyAttribute(lambda obj: obj.created_at)
    last_seen_at = factory.LazyAttribute(lambda obj: obj.created_at)


class EventFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Event

    id = factory.LazyFunction(lambda: uuid4())
    project = factory.SubFactory(ProjectFactory)
    raw_event = factory.SubFactory(
        RawEventFactory,
        id=factory.SelfAttribute("..id"),
        project=factory.SelfAttribute("..project"),
        created_at=factory.SelfAttribute("..created_at"),
        updated_at=factory.SelfAttribute("..updated_at"),
    )
    timestamp = factory.LazyFunction(
        lambda: datetime.utcnow().replace(tzinfo=timezone.utc)
    )
    platform = "python"
    message = factory.Sequence(lambda n: f"event message {n}")
    resolved = False
    resolved_at = None
    created_at = factory.LazyFunction(
        lambda: datetime.utcnow().replace(tzinfo=timezone.utc)
    )
    updated_at = factory.LazyAttribute(lambda obj: obj.created_at)
    issue = factory.SubFactory(
        EventIssueFactory,
        project=factory.SelfAttribute("..project"),
        primary_event_id=factory.SelfAttribute("..id"),
    )


class IssueFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Issue

    signature = "signature"
    project = factory.SubFactory(ProjectFactory)
    resolved = False
    resolved_at = None
    primary_event = factory.SubFactory(
        EventFactory, project=factory.SelfAttribute("..project"), issue=None
    )
    created_at = factory.LazyFunction(
        lambda: datetime.utcnow().replace(tzinfo=timezone.utc)
    )
    updated_at = factory.LazyAttribute(lambda obj: obj.created_at)
    first_seen_at = factory.LazyAttribute(lambda obj: obj.created_at)
    last_seen_at = factory.LazyAttribute(lambda obj: obj.created_at)
