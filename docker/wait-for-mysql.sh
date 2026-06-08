#!/bin/sh
# =============================================================================
# wait-for-mysql.sh
# Polls the MySQL host with `mysqladmin ping` until it responds, or fails
# after MAX_ATTEMPTS. Intended to be called by entrypoint.sh.
#
# Environment variables expected:
#   DB_HOST         - hostname of the MySQL service (default: db)
#   DB_PORT         - port (default: 3306)
#   MYSQL_ROOT_USER - username (default: root)
#   MYSQL_ROOT_PASSWORD - password (default: empty)
#   MAX_ATTEMPTS    - number of polls before giving up (default: 30)
#   SLEEP_SECONDS   - sleep between polls (default: 2)
# =============================================================================
set -eu

DB_HOST="${DB_HOST:-db}"
DB_PORT="${DB_PORT:-3306}"
MYSQL_ROOT_USER="${MYSQL_ROOT_USER:-root}"
# pymysql uses empty-string password for no password; mysqladmin also accepts
# an empty -p, but to avoid the interactive prompt, we pass an explicit empty
# string only when the password is unset.
if [ -z "${MYSQL_ROOT_PASSWORD:-}" ]; then
    PING_CMD="mysqladmin ping -h ${DB_HOST} -P ${DB_PORT} -u ${MYSQL_ROOT_USER}"
else
    PING_CMD="mysqladmin ping -h ${DB_HOST} -P ${DB_PORT} -u ${MYSQL_ROOT_USER} -p${MYSQL_ROOT_PASSWORD}"
fi

MAX_ATTEMPTS="${MAX_ATTEMPTS:-30}"
SLEEP_SECONDS="${SLEEP_SECONDS:-2}"

echo "wait-for-mysql: pinging ${DB_HOST}:${DB_PORT} as ${MYSQL_ROOT_USER} (max ${MAX_ATTEMPTS} attempts)"

attempt=1
while [ "$attempt" -le "$MAX_ATTEMPTS" ]; do
    if ${PING_CMD} >/dev/null 2>&1; then
        echo "wait-for-mysql: MySQL is up after ${attempt} attempt(s)."
        exit 0
    fi
    echo "wait-for-mysql: attempt ${attempt}/${MAX_ATTEMPTS} - not ready, sleeping ${SLEEP_SECONDS}s"
    sleep "${SLEEP_SECONDS}"
    attempt=$((attempt + 1))
done

echo "wait-for-mysql: ERROR - MySQL did not become ready in time." >&2
exit 1
