## Docker Compose Deployment

This document describes how to run Mise locally with Docker Compose in:

- **Core stack**: operational MVP workflow
- **Full stack**: broader platform dependencies

---

### 1. Core Stack

File: `infra/docker/docker-compose.core.yml`

Core stack includes:

- Per-service PostgreSQL containers:
  - `postgres-keycloak`
  - `postgres-restaurant`
  - `postgres-menu`
  - `postgres-order`
  - `postgres-kitchen`
- `dragonfly`, `nats`, `keycloak`, `traefik`
- Core domain services: `restaurant-svc`, `menu-svc`, `order-svc`, `kitchen-svc`
- `mise-web` and `mise-docs`

#### 1.1 Provisioning Strategy (Clean / Deterministic)

Provisioning uses one-shot jobs:

1. **DB creation**: handled by each Postgres container via `POSTGRES_DB`.
2. **Schema migration**: `migrate-*` jobs run `alembic upgrade head`.
3. **Data seed**: `seed-restaurant` and `seed-menu` jobs insert idempotent demo data.
4. **Keycloak seed**: realm/users/roles imported from `infra/keycloak/mise-realm.json` on startup (`--import-realm`).

Service startup is decoupled from migrations.

#### 1.2 Start

```bash
make up-core
```

Or:

```bash
docker compose -f infra/docker/docker-compose.core.yml up -d --build
```

#### 1.3 Run Provisioning Jobs Manually

```bash
make init-db   # runs migrate-restaurant/menu/order/kitchen
make seed      # runs seed-restaurant + seed-menu
```

#### 1.4 Endpoints

- Web: `http://localhost:3000`
- Docs (direct): `http://localhost:3010`
- Docs (Traefik): `http://localhost/docs`
- Keycloak: `http://localhost:8080/auth`
- Traefik dashboard: `http://localhost:8081`

#### 1.5 Stop

```bash
make down
```

---

### 2. Full Stack

File: `infra/docker/docker-compose.full.yml`

Full stack extends core with infrastructure and additional services (analytics/search/object storage and non-core domain services).

Start:

```bash
docker compose -f infra/docker/docker-compose.full.yml up -d --build
```

---

### 3. Operational Notes

- Seed jobs are idempotent and safe to rerun.
- Migration jobs are safe to rerun; Alembic tracks revision state.
- For a full local reset:

```bash
docker compose -f infra/docker/docker-compose.core.yml down -v
make up-core
```
