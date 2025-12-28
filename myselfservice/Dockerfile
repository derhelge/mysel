FROM python:3.12-slim AS base

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# System-Dependencies und Build-Tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    libcairo2-dev \
    libgirepository1.0-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# uv installieren
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Requirements installieren
COPY requirements.txt .
RUN uv pip install --system -r requirements.txt

# Development Stage
FROM base AS development
COPY docker-entrypoint.sh /
RUN chmod +x /docker-entrypoint.sh
ENTRYPOINT ["/docker-entrypoint.sh"]
#COPY . .
#CMD ["uvicorn", "config.asgi:application", "--host", "0.0.0.0", "--port", "8000", "--reload"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# Production Stage
FROM base AS production
RUN uv pip install --system gunicorn
COPY docker-entrypoint.prod.sh /
RUN chmod +x /docker-entrypoint.prod.sh
ENTRYPOINT ["/docker-entrypoint.prod.sh"]
COPY . .
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120", "config.wsgi:application"]
