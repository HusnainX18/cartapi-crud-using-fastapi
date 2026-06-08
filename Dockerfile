# syntax=docker/dockerfile:1.7
# =============================================================================
# CartAPI - Multi-stage Dockerfile
# =============================================================================
# Stage 1 (builder)  : compile wheels into /wheels with gcc + libffi
# Stage 2 (runtime)  : python:3.12-slim + wheels only + non-root appuser
# Final image target : < 200 MB, runs as `appuser`, exposes 8000
# =============================================================================

# -----------------------------------------------------------------------------
# Stage 1: builder
# -----------------------------------------------------------------------------
FROM python:3.12-slim AS builder

WORKDIR /build

# System deps needed only to build wheels (cryptography pulls in libffi/rust
# toolchain on some architectures). Stripped from the final image.
RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc \
        libffi-dev \
        pkg-config \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Build wheels into /wheels (NOT installed into the builder's site-packages).
# --no-cache-dir keeps the builder layer small.
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt


# -----------------------------------------------------------------------------
# Stage 2: runtime
# -----------------------------------------------------------------------------
FROM python:3.12-slim

WORKDIR /app

# Runtime-only system deps:
#   default-mysql-client : provides `mysqladmin` for the healthcheck script
#   curl                  : used in entrypoint readiness check
RUN apt-get update && apt-get install -y --no-install-recommends \
        default-mysql-client \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user. --create-home gives /home/appuser for any state,
# --shell lets us chown files we copy. UID 1000 matches the typical
# host user, so bind-mounts (in dev override) work cleanly.
RUN groupadd --gid 1000 appuser \
    && useradd --uid 1000 --gid 1000 --create-home --shell /bin/bash appuser

# Install Python deps from the prebuilt wheels (no network, no compilation).
COPY --from=builder /wheels /wheels
COPY requirements.txt .
RUN pip install --no-cache-dir --no-index --find-links /wheels -r requirements.txt \
    && rm -rf /wheels /root/.cache

# Copy application code and Alembic migration files.
COPY --chown=appuser:appuser app/ ./app/
COPY --chown=appuser:appuser alembic.ini ./alembic.ini
COPY --chown=appuser:appuser migrations/ ./migrations/
COPY --chown=appuser:appuser docker/entrypoint.sh ./docker/entrypoint.sh
COPY --chown=appuser:appuser docker/wait-for-mysql.sh ./docker/wait-for-mysql.sh

# Ensure the scripts are executable. (git on Windows can strip the +x bit.)
RUN chmod +x ./docker/entrypoint.sh ./docker/wait-for-mysql.sh

# Pre-create writable runtime directories and hand them to `appuser`.
# `app/core/logger.py` does `Path("logs").mkdir(exist_ok=True)` at import time
# when LOG_TO_FILE=True (enabled by docker-compose.override.yml in dev).
# /app itself is owned by root (from WORKDIR), so appuser cannot create
# subdirectories under it unless we make them in advance.
RUN mkdir -p /app/logs \
    && chown -R appuser:appuser /app/logs

# Drop privileges. From here on, every process is `appuser`.
USER appuser

# Document the port (purely informational; `EXPOSE` does NOT publish the port).
EXPOSE 8000

# Healthcheck for `docker ps` and for other services to gate on.
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD curl -fsS http://localhost:8000/ || exit 1

# Default command. The entrypoint handles "wait for MySQL -> migrate -> serve".
CMD ["./docker/entrypoint.sh"]
