#!/usr/bin/env bash
# init-db.sh — run one-shot migration jobs for core services.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
COMPOSE_FILE="${ROOT_DIR}/infra/docker/docker-compose.core.yml"

echo "==> Running Alembic migration jobs (restaurant/menu/order/kitchen)"
docker compose -f "${COMPOSE_FILE}" up --build \
  migrate-restaurant \
  migrate-menu \
  migrate-order \
  migrate-kitchen

echo "==> Migrations completed."
