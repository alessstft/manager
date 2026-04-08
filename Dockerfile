FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY tasks/ ./tasks/

RUN mkdir -p /app/data /app/tasks/media /app/tasks/staticfiles

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

WORKDIR /app/tasks

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
