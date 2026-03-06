#!/usr/bin/env bash
# seed-data.sh — run one-shot seed jobs for core demo data.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
COMPOSE_FILE="${ROOT_DIR}/infra/docker/docker-compose.core.yml"

echo "==> Running core seed jobs (restaurant/menu)"
docker compose -f "${COMPOSE_FILE}" up seed-restaurant seed-menu

echo "==> Seed jobs completed."
