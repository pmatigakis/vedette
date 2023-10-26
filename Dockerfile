FROM python:3.10.12
WORKDIR /app

ADD vedette /app/vedette
ADD events /app/events
ADD web /app/web
ADD api /app/api
COPY manage.py /app
COPY pyproject.toml /app
COPY docker-entrypoint.sh /app

RUN pip install poetry==1.4.2
RUN poetry config virtualenvs.create false
RUN poetry install --without dev

EXPOSE 8000

ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["web"]
