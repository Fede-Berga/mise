# Quickstart (Docker Core)

## Prerequisites

- Docker Desktop (or compatible Docker engine)
- Docker Compose v2
- `make`
- 8 GB RAM recommended

## 1. Configure Environment

```bash
cp .env.example .env
```

Keep default values for first run unless you need custom hostnames/ports.

## 2. Start the Core Stack

```bash
make up-core
```

This starts:

- `mise-web` (Next.js cockpit)
- `restaurant-svc`, `menu-svc`, `order-svc`, `kitchen-svc`
- `keycloak`, `nats`, `dragonfly`, dedicated PostgreSQL instances, `traefik`

## 3. Validate Health

```bash
curl -sf http://localhost:8001/healthz
curl -sf http://localhost:8002/healthz
curl -sf http://localhost:8003/healthz
curl -sf http://localhost:8004/healthz
curl -sf http://localhost:3000
```

Expected:

- service endpoints return JSON with `"status":"ok"`
- web root redirects to `/login` when unauthenticated

## 4. Open the Cockpit

- URL: `http://localhost:3000`
- Log in through Keycloak

## 5. Open Platform Docs (Containerized)

- URL (direct): `http://localhost:3010`
- URL (Traefik): `http://localhost/docs`
- Served by the `mise-docs` container through Traefik

## 6. Stop the Stack

```bash
make down
```
