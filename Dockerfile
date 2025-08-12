# syntax=docker/dockerfile:1

FROM python:3.13-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# System deps (optional; keep minimal for slim image)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt ./
RUN pip install -r requirements.txt

# Copy source
COPY app ./app
COPY tests ./tests
COPY pytest.ini ./pytest.ini

# Expose API port
EXPOSE 8000

# Default database can be overridden via env DISCOUNT_DB_URL
# e.g., -e DISCOUNT_DB_URL=sqlite:////data/discounts.db

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
