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
