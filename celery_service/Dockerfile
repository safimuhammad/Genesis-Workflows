FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies
COPY celery_service/requirements.txt .


RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project files
COPY ./celery_service /app


# Set PYTHONPATH to include /app/celery_service
ENV PYTHONPATH=/app/celery_service
WORKDIR /app/celery_service

EXPOSE 5555
COPY ./celery_service/start.sh /app/start.sh
RUN chmod +x /app/start.sh

CMD ["/app/start.sh"]  
# CMD ["celery", "-A", "config.celery_config.celery_app", "worker", "--loglevel=info"]