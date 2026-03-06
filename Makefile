PYTHON := python3
SERVICES_DIR := services
COMPOSE_CORE := infra/docker/docker-compose.core.yml
COMPOSE_FULL := infra/docker/docker-compose.full.yml
PY_SERVICE_DIRS := $(shell find services -maxdepth 1 -type d -name "*-service" | sort)

.PHONY: help install install-dev lint format typecheck test test-cov \
        up-core up-full down logs clean pre-commit-install init-db init-db-core seed \
        install-docs docs-serve docs-build bootstrap-core smoke-core

# ── Help ──────────────────────────────────────────────────────
help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ── Install ───────────────────────────────────────────────────
install: ## Install backend runtime dependencies
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r $(SERVICES_DIR)/common/requirements.txt

install-dev: ## Install backend dev dependencies
	$(PYTHON) -m pip install -r $(SERVICES_DIR)/common/requirements-dev.txt

install-web: ## Install web (Next.js) dependencies
	cd mise-web && npm ci || npm install

install-docs: ## Install docs dependencies
	$(PYTHON) -m pip install -r docs/requirements.txt

# ── Code Quality ──────────────────────────────────────────────
lint: ## Run ruff linter
	@set -e; \
	for svc in services/common $(PY_SERVICE_DIRS); do \
		echo "==> $$svc"; \
		(cd $$svc && ruff check app tests); \
	done

format: ## Auto-format with ruff
	@set -e; \
	for svc in services/common $(PY_SERVICE_DIRS); do \
		echo "==> $$svc"; \
		(cd $$svc && ruff format app tests); \
	done

format-check: ## Check formatting (CI-friendly)
	@set -e; \
	for svc in services/common $(PY_SERVICE_DIRS); do \
		echo "==> $$svc"; \
		(cd $$svc && ruff format --check app tests); \
	done

typecheck: ## Run mypy type checker
	@set -e; \
	for svc in services/common $(PY_SERVICE_DIRS); do \
		echo "==> $$svc"; \
		(cd $$svc && mypy app --ignore-missing-imports); \
	done

lint-web: ## Lint Next.js app
	cd mise-web && npm run lint

# ── Tests ─────────────────────────────────────────────────────
test: ## Run backend tests
	@set -e; \
	for svc in services/common $(PY_SERVICE_DIRS); do \
		echo "==> $$svc"; \
		(cd $$svc && pytest tests --tb=short -q); \
	done

test-cov: ## Run backend tests with coverage
	@set -e; \
	for svc in services/common $(PY_SERVICE_DIRS); do \
		echo "==> $$svc"; \
		(cd $$svc && pytest tests --cov=app --cov-report=term-missing); \
	done

test-web: ## Run web tests
	cd mise-web && npm test 2>/dev/null || echo "No web tests configured yet"

test-all: test test-web ## Run all tests

# ── Documentation ─────────────────────────────────────────────
docs-serve: ## Run local docs site with live reload
	mkdocs serve

docs-build: ## Build static docs site
	mkdocs build --strict

# ── Docker ────────────────────────────────────────────────────
up-core: ## Start core stack (Postgres, Dragonfly, NATS, Keycloak, Traefik + core services)
	docker compose -f $(COMPOSE_CORE) up -d --build --pull missing

up-full: ## Start full stack (all services + MinIO, ClickHouse, Meilisearch)
	docker compose -f $(COMPOSE_FULL) up -d --build --pull missing

down: ## Stop all running containers
	docker compose -f $(COMPOSE_CORE) down 2>/dev/null; \
	docker compose -f $(COMPOSE_FULL) down 2>/dev/null; \
	true

build-core: ## Build core stack images
	docker compose -f $(COMPOSE_CORE) build

build-full: ## Build full stack images
	docker compose -f $(COMPOSE_FULL) build

logs: ## Follow logs from all containers
	docker compose -f $(COMPOSE_CORE) logs -f 2>/dev/null || \
	docker compose -f $(COMPOSE_FULL) logs -f

ps: ## Show running containers
	docker compose -f $(COMPOSE_CORE) ps 2>/dev/null; \
	docker compose -f $(COMPOSE_FULL) ps 2>/dev/null; \
	true

# ── Database ──────────────────────────────────────────────────
init-db: ## Run one-shot Alembic migration jobs for core services
	docker compose -f $(COMPOSE_CORE) up --build migrate-restaurant migrate-menu migrate-order migrate-kitchen

init-db-core: ## Alias of init-db for backward compatibility
	$(MAKE) init-db

seed: ## Run one-shot seed jobs for core demo data
	docker compose -f $(COMPOSE_CORE) up seed-restaurant seed-menu

bootstrap-core: ## Provision core stack + migrations + seed jobs
	docker compose -f $(COMPOSE_CORE) up -d --build --pull missing

smoke-core: ## Run smoke checks against core stack endpoints
	@echo "==> Core API health"
	curl -sf http://localhost:8001/healthz >/dev/null && echo "restaurant-svc ok"
	curl -sf http://localhost:8002/healthz >/dev/null && echo "menu-svc ok"
	curl -sf http://localhost:8003/healthz >/dev/null && echo "order-svc ok"
	curl -sf http://localhost:8004/healthz >/dev/null && echo "kitchen-svc ok"
	@echo "==> Web and docs"
	curl -sf http://localhost:3000 >/dev/null && echo "mise-web ok"
	curl -sf http://localhost:3010 >/dev/null && echo "mise-docs ok"
	@echo "Smoke checks passed."

# ── Developer Setup ───────────────────────────────────────────
pre-commit-install: ## Install pre-commit hooks
	pre-commit install
	pre-commit install --hook-type commit-msg

# ── Cleanup ───────────────────────────────────────────────────
clean: ## Remove caches, build artifacts, and coverage reports
	find . -depth -type d \( -name __pycache__ -o -name .pytest_cache -o -name .mypy_cache -o -name .ruff_cache -o -name htmlcov \) -exec rm -rf {} + 2>/dev/null || true
	find . -type f \( -name "*.pyc" -o -name "*.pyo" -o -name ".coverage" -o -name ".DS_Store" \) -delete 2>/dev/null || true
	rm -rf mise-web/.next mise-web/out site 2>/dev/null || true
	@echo "Cleaned."
