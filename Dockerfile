FROM python:3.11-slim

# Metadata
LABEL maintainer="FinOps Team"
LABEL description="GCP FinOps Reporting Suite"

# System dependencies for matplotlib & reportlab
RUN apt-get update && apt-get install -y \
    cron \
    curl \
    build-essential \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    fonts-dejavu \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app/backend

# Install Python dependencies
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ ./
COPY .env.example /app/.env

# Create output directories
RUN mkdir -p /app/outputs/cost_reports/charts \
    /app/outputs/finops_reports/charts \
    /app/outputs/logs

# Copy and configure cron job (if exists)
RUN if [ -f /app/cron/weekly-report-cron ]; then \
    cp /app/cron/weekly-report-cron /etc/cron.d/finops-cron && \
    chmod 0644 /etc/cron.d/finops-cron && \
    crontab /etc/cron.d/finops-cron && \
    touch /var/log/finops-reports.log; \
    fi

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV GOOGLE_APPLICATION_CREDENTIALS=/credentials/gcp-sa.json
ENV PYTHONPATH=/app/backend

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:9006/health || exit 1

# Default command - run from /app/backend so relative imports resolve
CMD ["uvicorn", "api.api:app", "--host", "0.0.0.0", "--port", "9006", "--workers", "2", "--proxy-headers"]
