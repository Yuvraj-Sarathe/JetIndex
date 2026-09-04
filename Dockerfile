FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

# System deps for Playwright
ARG INSTALL_PLAYWRIGHT=true
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl wget gnupg \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Playwright (optional, controlled by build-arg)
RUN if [ "$INSTALL_PLAYWRIGHT" = "true" ]; then \
        playwright install --with-deps chromium; \
    fi

# Copy application code
COPY . .

# Default: run API
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
