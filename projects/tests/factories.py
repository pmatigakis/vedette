from datetime import datetime, timezone
from uuid import uuid4

import factory

from projects.models import Project


class ProjectFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Project

    name = factory.Sequence(lambda n: f"project-{n}")
    public_key = factory.LazyFunction(lambda: uuid4())
    created_at = factory.LazyFunction(
        lambda: datetime.utcnow().replace(tzinfo=timezone.utc)
    )
    updated_at = factory.LazyAttribute(lambda obj: obj.created_at)
