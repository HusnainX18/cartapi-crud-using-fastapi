#!/bin/bash
set -euo pipefail

ACTIVE_COLOR_FILE=".active_color"
NGINX_CONF_DIR="docker/nginx/dynamic"
NGINX_CONF_FILE="$NGINX_CONF_DIR/active_backend.conf"

echo "==> Determining active environment..."
if [ -f "$ACTIVE_COLOR_FILE" ]; then
    ACTIVE=$(cat "$ACTIVE_COLOR_FILE")
else
    ACTIVE="blue"
fi

if [ "$ACTIVE" = "blue" ]; then
    INACTIVE="green"
else
    INACTIVE="blue"
fi

echo "Active environment: $ACTIVE"
echo "Target environment for deployment: $INACTIVE"

echo "==> Pulling latest image for api-$INACTIVE..."
docker compose -f docker-compose.prod.yml pull api-$INACTIVE

echo "==> Starting container for api-$INACTIVE..."
docker compose -f docker-compose.prod.yml up -d --no-deps --force-recreate api-$INACTIVE

echo "==> Waiting for api-$INACTIVE to become healthy..."
HEALTHY=false
for i in $(seq 1 12); do
    STATUS=$(docker inspect --format='{{json .State.Health.Status}}' cartapi-api-$INACTIVE 2>/dev/null || echo "unknown")
    if [ "$STATUS" = "\"healthy\"" ]; then
        echo "api-$INACTIVE is healthy!"
        HEALTHY=true
        break
    fi
    echo "Waiting for healthcheck... current status: $STATUS"
    sleep 5
done

if [ "$HEALTHY" = false ]; then
    echo "Error: api-$INACTIVE did not become healthy in time."
    docker compose -f docker-compose.prod.yml logs api-$INACTIVE
    exit 1
fi

echo "==> Applying migrations from api-$INACTIVE container..."
docker compose -f docker-compose.prod.yml exec -T api-$INACTIVE alembic upgrade head

echo "==> Swapping traffic in Nginx config..."
mkdir -p "$NGINX_CONF_DIR"
cat <<EOF > "$NGINX_CONF_FILE"
upstream cartapi_backend {
    server api-$INACTIVE:8000;
}
EOF

echo "==> Ensuring Nginx container is running..."
docker compose -f docker-compose.prod.yml up -d nginx

echo "==> Reloading Nginx..."
docker compose -f docker-compose.prod.yml exec -T nginx nginx -s reload

echo "==> Updating active color file to $INACTIVE..."
echo "$INACTIVE" > "$ACTIVE_COLOR_FILE"

echo "==> Stopping old active environment (api-$ACTIVE)..."
docker compose -f docker-compose.prod.yml stop api-$ACTIVE

echo "==> Deployment of api-$INACTIVE completed successfully!"
