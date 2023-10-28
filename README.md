# Vedette

Vedette is an error reporting application that is partially compatible with Sentry's
Python client.

This application is at a very early alpha stage. Many things haven't been properly
tested and a lot of features that are available in Sentry are missing. 

## Requirements

The following applications are required.

* PostgreSQL version 12 or higher. It is recommended to use PostgreSQL 15.3
* RabbitMQ version 3.5 or higher
* Docker

## Installation

Build the Vedette docker image.

```bash
docker build -t vedette .
```

Make a copy of the environment variable template file `env/env_template` and
change the variables according to your needs.

Run the database migrations.

```bash
docker run --rm --env-file .env vedette migrate
```

Build the static files.

```bash
docker run --rm --env-file .env --mount source=vedette-static,target=/app/static vedette python manage.py collectstatic --noinput --clear 
```

Start the celery worker.

```bash
docker run --env-file .env --name vedette-workers vedette workers
```

Start the web server.

```bash
docker run --env-file .env --name vedette-web -p 8000:8000 --mount source=vedette-static,target=/app/static,ro vedette web
```

Create an administrator account.

```bash
docker exec -it vedette-web python manage.py createsuperuser
```

Create a project.

```bash
docker exec -it vedette-web python manage.py createproject <project-name>
```

The application will return the project id and public key. Use them in the
Sentry client. 

```python
import logging
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration

sentry_logging = LoggingIntegration(
    level=logging.INFO,
    event_level=logging.ERROR

)

sentry_sdk.init(
    dsn="http://<project-public-key>@localhost:8000/<project-id>",
    integrations=[sentry_logging]
)
```
