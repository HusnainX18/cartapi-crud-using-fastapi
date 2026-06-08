#!/bin/bash
# =============================================================================
# deploy.sh — deploy the latest CartAPI to this EC2 instance
# =============================================================================
# Usage:
#   ./deploy.sh
#
# Prerequisites:
#   - docker + compose plugin installed (see ec2_bootstrap.sh)
#   - .env file exists with MYSQL_ROOT_PASSWORD (and optional MYSQL_DATABASE)
#   - docker-compose.prod.yml is in the same directory
#   - The ubuntu user can run docker (logged out and back in after bootstrap)
#
# What it does:
#   1. Pull the latest image from DockerHub (husnaib/cartapi:latest)
#   2. Start (or restart) the stack via docker-compose.prod.yml
#   3. Run alembic upgrade head (migrations — idempotent)
#   4. Healthcheck the API, failing loudly if it doesn't respond
# =============================================================================
set -eu

echo "==> deploy: starting at $(date -u)"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# ---- Check for .env ----
if [ ! -f .env ]; then
    echo "WARNING: .env not found. Ensure MYSQL_ROOT_PASSWORD is exported."
fi

# ---- Step 1: Pull the latest image ----
echo "==> Pulling husnaib/cartapi:latest"
docker pull husnaib/cartapi:latest

# ---- Step 2: Start (or restart) the stack ----
echo "==> Starting services (docker compose -f docker-compose.prod.yml up -d)"
docker compose -f docker-compose.prod.yml up -d

# ---- Step 3: Migrations ----
echo "==> Running alembic upgrade head"
# Wait for the api container to be healthy before running migrations
for i in $(seq 1 12); do
    if docker compose -f docker-compose.prod.yml exec -T api \
        curl -fsS http://localhost:8000/ > /dev/null 2>&1; then
        break
    fi
    echo "  waiting for api container... ($i/12)"
    sleep 5
done

docker compose -f docker-compose.prod.yml exec -T api alembic upgrade head
echo "  Migrations applied."

# ---- Step 4: Healthcheck ----
echo "==> Healthcheck"
for i in $(seq 1 6); do
    if curl -fsS http://localhost:8000/ > /dev/null 2>&1; then
        echo "  API is UP: $(curl -fsS http://localhost:8000/)"
        echo "==> deploy: successful"
        exit 0
    fi
    echo "  waiting for API... ($i/6)"
    sleep 5
done

# Healthcheck failed — dump logs and exit non-zero
echo "ERROR: API healthcheck failed" >&2
docker compose -f docker-compose.prod.yml logs --tail 30 api
exit 1
