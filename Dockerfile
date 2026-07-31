<<<<<<< HEAD
# Production image for auto-repair-shop-api (Gunicorn).
# Local/dev still uses the shared django-runtime bind-mount workflow.
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV VIRTUAL_ENV=/app/venv
ENV PATH="${VIRTUAL_ENV}/bin:${PATH}"
ENV DJANGO_SETTINGS_MODULE=config.settings.production
ENV REQUIREMENTS_FILE=production.txt

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN python -m venv "${VIRTUAL_ENV}" \
    && pip install --no-cache-dir --upgrade pip

COPY requirements/ /app/requirements/
RUN pip install --no-cache-dir -r "/app/requirements/${REQUIREMENTS_FILE}"

COPY . /app/

EXPOSE 8000
STOPSIGNAL SIGTERM
ENTRYPOINT ["/bin/sh", "/app/docker/entrypoint-app.sh"]
=======
FROM python:3.12-slim-bookworm
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /app
RUN apt-get update \
    && apt-get install -y --no-install-recommends bash curl netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY . /app
RUN chmod +x /app/docker/entrypoint.sh /app/docker/wait-for.sh /app/docker/stop-stack.sh
RUN adduser --disabled-password --gecos "" --uid 1000 appuser \
    && mkdir -p /app/staticfiles /app/media \
    && chown -R appuser:appuser /app
USER appuser
EXPOSE 8000
ENTRYPOINT ["/app/docker/entrypoint.sh"]
CMD ["gunicorn", "config.wsgi:application", "-c", "/app/docker/gunicorn.conf.py"]
>>>>>>> 57e364fbf09a38203cf48b12a33136d53157d211
