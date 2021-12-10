FROM python:3.9.4
WORKDIR /app

ADD vedette /app/vedette
ADD projects /app/projects
ADD events /app/events
ADD web /app/web
ADD api /app/api
COPY manage.py /app
COPY pyproject.toml /app
COPY docker-entrypoint.sh /app

RUN pip install poetry==1.1.4
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev

EXPOSE 8000

ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["web"]
