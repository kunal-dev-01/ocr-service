# ============================================================================
# FILE: services/ocr-service/Dockerfile
# PURPOSE: Production with shared package support
# ============================================================================

# ============================================================================
# STAGE 1: PYTHON BUILDER (Install dependencies)
# ============================================================================

FROM python:3.11-slim AS python-builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    pkg-config gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy shared queue package (relative to ROOT context)
WORKDIR /build
COPY packages/zemrev-queue ./packages/zemrev-queue
RUN pip install ./packages/zemrev-queue

# Copy service requirements (relative to ROOT context)
COPY services/ocr-service/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# ============================================================================
# STAGE 2: RUNTIME (Minimal)
# ============================================================================

FROM python:3.11-slim

# Install Tesseract + runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    libtesseract-dev \
    curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Verify Tesseract
RUN tesseract --version

# Copy Python packages from builder
COPY --from=python-builder /usr/local /usr/local

ENV PATH=/root/.local/bin:$PATH

# Non-root user
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app && \
    chown -R appuser:appuser /app && \
    mkdir -p /tmp/zemrev_ocr_uploads && \
    chown -R appuser:appuser /tmp/zemrev_ocr_uploads

WORKDIR /app

# Copy application code (relative to ROOT context)
COPY --chown=appuser:appuser services/ocr-service/ .

USER appuser

EXPOSE 8004

HEALTHCHECK --interval=60s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://34.141.19.200:8004/health || exit 1

CMD ["python", "-m", "uvicorn", "app.main:app", \
     "--host", "0.0.0.0", \
     "--port", "8004", \
     "--workers", "2", \
     "--log-level", "info"]
