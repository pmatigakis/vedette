# Starting the application

Start the development server.
```bash
ENV_PATH=env/.env ./manage.py runserver
```

Start the celery workers.
```bash
ENV_PATH=env/.env celery -A vedette worker -l INFO
```
