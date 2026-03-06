## Extensibility & Community Contributions

Mise is designed to be a **platform**, not a monolith. This guide explains how to extend it safely:

- Add new microservices
- Extend existing ones
- Keep single- and multi-restaurant deployments intact

---

### 1. Principles

- **Isolation by default**
  - Each service owns its DB schema
  - No cross-service DB queries
- **Events over tight coupling**
  - Use NATS JetStream subjects for cross-service communication
- **Tenant safety**
  - Always carry `tenant_id` in data and events
  - Enforce RLS in PostgreSQL

---

### 2. Adding a New Service

Example: `loyalty-service`

1. **Create the service skeleton**
   - Directory: `services/loyalty-service/`
   - Tech: FastAPI + SQLAlchemy + Alembic
   - DB schema: `loyalty_svc` in PostgreSQL
2. **Define contracts**
   - REST endpoints (`/api/v1/loyalty/...`)
   - NATS subjects:
     - `mise.loyalty.points_awarded`
     - `mise.loyalty.tier_changed`
   - Events consumed:
     - `mise.order.closed`
3. **Update deployment**
   - Docker:
     - Add service to `infra/docker/docker-compose.full.yml` (and core if relevant)
   - Kubernetes:
     - Add a Helm chart under `infra/helm/charts/mise-loyalty-svc/`
     - Wire into umbrella chart `infra/helm/mise-platform`
4. **Document**
   - Update `docs/architecture/overview.md` (brief mention)
   - Add a section to this file with:
     - Endpoints
     - NATS subjects
     - Required env vars

---

### 3. Single vs Multi-Restaurant Safety

When adding or changing features:

- **Always include `tenant_id`**
  - In DB tables
  - In NATS event payloads
- **Guard read/write paths**
  - Extract `tenant_id` from JWT
  - Set `app.current_tenant` in DB session
  - Rely on PostgreSQL RLS as a hard backstop

This ensures:

- A single-restaurant owner can safely run Mise on one machine
- A SaaS operator can host many restaurants without data leaks

---

### 4. Updating Docker Compose

When you add a new service:

- **Core-only feature** (essential for basic operations)
  - Add it to `infra/docker/docker-compose.core.yml` and `infra/docker/docker-compose.full.yml`
- **Advanced/optional feature**
  - Add it only to `infra/docker/docker-compose.full.yml`

Keep service names and env var patterns consistent:

- DB URL: `DATABASE_URL`
- Schema: `DATABASE_SCHEMA`
- NATS: `NATS_URL`
- Redis: `REDIS_URL`
- Keycloak: `KEYCLOAK_URL`, `KEYCLOAK_REALM`

---

### 5. Updating kind / Helm

For new services:

- Create a Helm chart:
  - `infra/helm/charts/mise-<name>-svc/`
  - Deployment, Service, HPA, config
- Register it in:
  - `infra/helm/mise-platform/Chart.yaml`
  - `infra/helm/mise-platform/values.yaml`

The `infra/kind/cluster-rocky.yaml` file does not need changes for each service; it only defines cluster shape and port mappings.

---

### 6. Contribution Checklist

- [ ] Service has its own DB schema and migrations
- [ ] All tables include `tenant_id` and RLS
- [ ] Events use consistent subject naming (`mise.<domain>.<entity>.<event>`)
- [ ] Docker Compose updated (core/full as appropriate)
- [ ] Helm chart added and referenced by umbrella chart
- [ ] Docs updated:
  - [ ] Architecture overview
  - [ ] This extensibility guide (section for new service)
  - [ ] Any feature-specific docs if needed
