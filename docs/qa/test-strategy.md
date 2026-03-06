# Test Strategy

## Goals

- Prevent regressions in auth, tenancy, and order lifecycle.
- Detect desynchronization between order and kitchen status.
- Keep fast feedback for local development and CI.

## Automated Tests

Current automated scope:

- Unit tests for kitchen/order status sync logic.
- Unit tests for JWT audience handling (`aud`/`azp` acceptance).

Run:

```bash
make test
```

## Recommended CI Gates

1. `make lint`
2. `make typecheck`
3. `make test`
4. `npm --prefix mise-web run build`
5. `mkdocs build --strict`

## Coverage Priorities

1. Auth and token refresh flows
2. Tenant routing and header enforcement
3. Order creation and kitchen ticket generation
4. Bidirectional status synchronization
5. Role-based access control in middleware and UI
