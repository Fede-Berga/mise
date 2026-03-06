## Mise Architecture Overview

This document summarizes the architecture of Mise and ties it to the deployment artifacts in this repo (Docker Compose and kind/Rocky).

---

### 1. High-Level Architecture

- **Client layer**: Next.js web, Expo mobile, KDS, POS
- **Gateway layer**: Traefik as ingress/API gateway, Keycloak for IAM
- **Microservices layer**: FastAPI services for restaurant, menu, orders, kitchen, inventory, personnel, finance, notifications, analytics, AI, hardware
- **Data layer**: PostgreSQL (per-service schemas + RLS), Dragonfly (Redis), NATS JetStream, ClickHouse, MinIO, Meilisearch

See the original architecture document for detailed ASCII diagrams and service responsibilities.

---

### 2. Multi-Tenancy

- Each restaurant is identified by a **tenant ID** and/or **Keycloak realm**
- All tables include a `tenant_id` column
- PostgreSQL Row-Level Security (RLS) enforces tenant separation
- Services:
  - Extract `tenant_id` from Keycloak JWT
  - Set `app.current_tenant` on DB connections

This works for:

- A single restaurant (one tenant)
- Many restaurants (hundreds of tenants) on the same cluster

---

### 3. Service Ownership

Each microservice:

- Owns its **PostgreSQL schema**
- Exposes a **REST API** (FastAPI)
- Talks to others via **NATS JetStream** events (no shared DB access)

Examples:

- `restaurant-service` — onboarding, restaurant profile, QR tables
- `menu-service` — menu items, modifiers, availability
- `order-service` — order lifecycle, WebSockets
- `kitchen-service` — ticket routing, KDS
- `inventory-service` — stock, recipes, auto-deduction

The Docker Compose and future Helm charts mirror this service breakdown.

---

### 4. Core vs Full Stack

- **Core**:
  - PostgreSQL, Dragonfly, NATS, Keycloak, Traefik
  - `restaurant-svc`, `menu-svc`, `order-svc`, `mise-web`
  - Goal: fast local dev for core workflows
- **Full**:
  - Core + MinIO, ClickHouse, Meilisearch
  - All microservices, including AI and analytics
  - Goal: integration testing and realistic on-prem deploys

The separation is reflected in:

- `infra/docker/docker-compose.core.yml` vs `infra/docker/docker-compose.full.yml`
- Future Helm values (`values-core.yaml` vs `values-full.yaml`)

---

### 5. AI & Analytics

- `ai-service` centralizes calls to Claude:
  - Customer chatbot
  - Menu generation
  - Forecasting
  - Scheduling assistant
- `analytics-service`:
  - Consumes all domain events from NATS
  - Writes to ClickHouse
  - Exposes dashboards and reports

In Docker Compose, these are optional but wired; in production Helm, you can toggle them per deployment.

---

### 6. Extensibility

Community contributors can:

- Add new services (e.g. loyalty, marketing) by:
  - Creating a FastAPI app + DB schema
  - Defining NATS subjects
  - Adding Dockerfiles + Compose/Helm entries
- Extend existing services (e.g. new inventory features) by:
  - Adding endpoints/events
  - Updating docs and contracts

See `docs/contributing/extensibility.md` for concrete steps and patterns.
