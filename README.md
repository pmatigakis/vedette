# Vedette

Vedette is an error reporting application that is partially compatible with Sentry's
Python client.

This application is at a very early alpha stage. Many things haven't been properly
tested and a lot of features that are available in Sentry are missing. 

## Requirements

The following applications are required.

* Postgres version 9.5 or greater
* RabbitMQ version 3.5 or greater
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
docker run --env-file .env vedette migrate
```

Start the celery worker

```bash
docker run --env-file .env --name vedette-workers vedette workers
```

Start the web server

```bash
docker run --env-file .env --name vedette-web -p 8000:8000 vedette web
```

Create an administrator account

```bash
docker exec -it vedette-web python manage.py createsuperuser
```

Create a project

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
