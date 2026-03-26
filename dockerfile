# ──────────────────────────────────────────────────
# Stage 1 – builder: compile C extensions
# ──────────────────────────────────────────────────
FROM python:3.11-slim AS builder

# gcc / g++ only needed to build wheels; discarded in final stage
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

COPY requirements.txt .

# Upgrade pip (CVE-2025-8869), wheel (CVE-2026-24049), and setuptools (CVE-2026-23949
# via vendored jaraco.context) before installing deps
RUN pip install --no-cache-dir --upgrade \
        pip==25.3 \
        wheel==0.46.2 \
        setuptools==82.0.1 \
    && pip install --no-cache-dir -r requirements.txt

# ──────────────────────────────────────────────────
# Stage 2 – runtime: lean final image
# ──────────────────────────────────────────────────
FROM python:3.11-slim

LABEL maintainer="localpdf.io"

# ghostscript is a runtime dependency; no build tools kept
RUN apt-get update && apt-get install -y --no-install-recommends \
    ghostscript \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip/wheel/setuptools in runtime stage so old base-image metadata
# (pip 24.0, wheel 0.45.1) is replaced before site-packages are overlaid
# CVE-2025-8869 (pip), CVE-2026-24049 (wheel), CVE-2026-23949 (jaraco.context via setuptools)
RUN pip install --no-cache-dir --upgrade \
        pip==25.3 \
        wheel==0.46.2 \
        setuptools==82.0.1

# Non-root user (AVD-DS-0002 HIGH)
RUN groupadd -r appuser && useradd -r -g appuser -d /app -s /sbin/nologin appuser

WORKDIR /app

# Copy only the installed Python packages from the builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages \
                    /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application source
COPY app.py .

# Create upload/output dirs with correct ownership
RUN mkdir -p uploads outputs && chown -R appuser:appuser /app

USER appuser

EXPOSE 5000

# Health-check via the root endpoint (AVD-DS-0026 LOW)
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/')" || exit 1

CMD ["python", "app.py"]
