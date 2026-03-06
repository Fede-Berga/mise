# Mise Platform

Mise is a multi-tenant restaurant operations platform built as a set of FastAPI microservices with a Next.js cockpit.  
The MVP focuses on one high-value workflow implemented end-to-end: **order entry, kitchen ticketing, and bidirectional status synchronization**.

## Product Scope (Current MVP)

- Role-based cockpit access (`owner`, `manager`, `chef`, `waiter`, `cashier`)
- Menu management
- Order creation from UI
- Automatic kitchen ticket generation from order events
- Order status and kitchen status synchronization (both directions)
- Tenant/restaurant context isolation through authenticated request forwarding

## Architecture Snapshot

### Services

- `restaurant-svc`
- `menu-svc`
- `order-svc`
- `kitchen-svc`
- shared library in `services/common`

### Platform Components

- `mise-web` (Next.js 14)
- `keycloak` for authentication and role claims
- `nats` (JetStream) for eventing
- per-service PostgreSQL instances
- `dragonfly` (Redis-compatible)
- `traefik`

### Core Event Subjects

- `mise.orders.placed`
- `mise.orders.status_changed`

## Repository Layout

- `services/` backend microservices and shared code
- `mise-web/` frontend cockpit
- `infra/docker/` local stack definitions
- `docs/` technical and operational documentation
- `mkdocs.yml` documentation site configuration

## Quickstart (Local)

### Prerequisites

- Docker + Docker Compose v2
- Python 3
- Node.js 24 (for local web development/builds)
- `make`

### Run

```bash
cp .env.example .env
make up-core
```

Provisioning jobs (if you want to run them explicitly):

```bash
make init-db
make seed
```

### Health Checks

```bash
curl -sf http://localhost:8001/healthz
curl -sf http://localhost:8002/healthz
curl -sf http://localhost:8003/healthz
curl -sf http://localhost:8004/healthz
curl -sf http://localhost:3000
```

### Access

- Cockpit: `http://localhost:3000`
- Docs (direct port): `http://localhost:3010`
- Docs (via Traefik): `http://localhost/docs`
- Keycloak: `http://localhost:8080`

Stop:

```bash
make down
```

## Development Workflow

### Install Tooling

```bash
make install-dev
make install-web
make install-docs
```

### Quality Gates

```bash
make lint
make typecheck
make test
npm --prefix mise-web run build
make docs-build
```

## Documentation (Open Source Stack)

Documentation is built with:

- [MkDocs](https://www.mkdocs.org/) (BSD)
- [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) (MIT)

Run locally:

```bash
make docs-serve
```

Build static site:

```bash
make docs-build
```

## Testing

### Automated

- Python unit tests (backend logic and auth validation)
- Next.js production build validation

Run:

```bash
make test
```

### Manual Release Checklist

Use [`docs/qa/e2e-checklist.md`](docs/qa/e2e-checklist.md) before tagging a release.

Key mandatory checks:

1. Login/session stability (no recurring `401`)
2. Role access matrix enforcement
3. Order -> kitchen ticket creation
4. Status sync consistency between Orders and Kitchen
5. Tenant isolation with restaurant switching

## Security and Multi-Tenancy

- JWT validation with Keycloak signing keys
- Audience/client validation (`aud` or `azp`)
- Tenant header enforcement and auth-aware request forwarding
- Role-based route protection in middleware

## Contributing

1. Create a branch from `develop` (or follow team workflow in docs).
2. Implement change with tests.
3. Run all local quality gates.
4. Open PR with clear scope and risk notes.

See:

- [`docs/engineering/git-workflow.md`](docs/engineering/git-workflow.md)
- [`docs/contributing/extensibility.md`](docs/contributing/extensibility.md)

## License

This project is released under the [GNU GPL v3.0 License](LICENSE).
