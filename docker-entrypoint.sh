#!/bin/bash
set -e

cd /app

if [ "$1" = "web" ]; then
    exec gunicorn --bind 0.0.0.0:8000 vedette.wsgi
elif [ "$1" = "workers" ]; then
    exec celery -A vedette worker -l INFO
elif [ "$1" = "migrate" ]; then
    exec python manage.py migrate
fi

exec "$@"
