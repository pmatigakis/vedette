FROM python:3.9.4
WORKDIR /app

ADD vedette /app/vedette
ADD projects /app/projects
ADD events /app/events
ADD web /app/web
ADD api /app/api
COPY manage.py /app
COPY requirements.txt /app
COPY docker-entrypoint.sh /app

RUN pip install -r requirements.txt

EXPOSE 8000

ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["web"]
