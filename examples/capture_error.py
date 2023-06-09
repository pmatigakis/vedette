import logging

import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration

PUBLIC_KEY = "<project-public-key>"
PROJECT_ID = "<project-id>"

sentry_logging = LoggingIntegration(
    level=logging.INFO, event_level=logging.ERROR
)

sentry_sdk.init(
    dsn=f"http://{PUBLIC_KEY}@localhost:8000/{PROJECT_ID}",
    integrations=[sentry_logging],
)

# Raise an exception
x = 12 / 0
