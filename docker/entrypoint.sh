#!/bin/sh
# =============================================================================
# entrypoint.sh - runs as `appuser` inside the api container
#
# Sequence:
#   1. Wait for MySQL to accept connections (so alembic doesn't crash)
#   2. Run `alembic upgrade head` (idempotent; safe to re-run on every boot)
#   3. exec the command passed as $1..$N, OR the default uvicorn command
#
# Why pass-through?
#   The dev override (docker-compose.override.yml) needs uvicorn with --reload,
#   while the production image just needs the stock uvicorn command. Instead
#   of duplicating the wait+migrate logic, we run those once here and then
#   hand off to whatever command the compose file / caller wants.
#
# Examples:
#   # default (production): ./docker/entrypoint.sh
#   # dev (override)      : ./docker/entrypoint.sh uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
#   # one-off shell       : ./docker/entrypoint.sh alembic revision --autogenerate -m "..."
# =============================================================================
set -eu

echo "==> entrypoint: starting at $(date -u +'%Y-%m-%dT%H:%M:%SZ')"

# Make sure we run migrations from the project root so alembic.ini is found.
cd /app

# Step 1: wait for the database.
./docker/wait-for-mysql.sh

# Step 2: apply migrations. `alembic upgrade head` is safe to run repeatedly;
# if the DB is already at head, this is a no-op.
echo "==> entrypoint: running alembic upgrade head"
alembic upgrade head

# Step 3: serve. If the caller passed a command, run it; otherwise default
# to the production uvicorn line. `exec` replaces the shell so the final
# process becomes PID 1 (signals from `docker stop` go straight to it).
if [ "$#" -gt 0 ]; then
    echo "==> entrypoint: exec $*"
    exec "$@"
else
    echo "==> entrypoint: starting uvicorn on 0.0.0.0:8000 (default)"
    exec uvicorn app.main:app --host 0.0.0.0 --port 8000
fi
