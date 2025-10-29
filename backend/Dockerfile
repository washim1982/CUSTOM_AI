# ---- Base ----
FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# System deps (curl for healthcheck; build tools only if needed)
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy application
COPY . .

# Install deps
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir gunicorn uvicorn



# Optional CORS domain injection: if CORS_ORIGINS provided, your app.main can read it.
# EXPOSE is informational; behind Nginx
EXPOSE 8000

# Healthcheck executed by docker-compose
HEALTHCHECK --interval=15s --timeout=5s --retries=5 CMD curl -fsS http://localhost:8000/api/health || exit 1

# Gunicorn + Uvicorn workers for production
# Tweak workers based on CPU cores: workers=2-4 is a good start
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-w", "2", "-b", "0.0.0.0:8000", "app.main:app"]
