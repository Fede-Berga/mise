## What does this PR do?

<!-- Brief description of the change and its motivation. -->

## Why?

<!-- Link to issue, Slack thread, or explain the business context. -->

## How to test

<!-- Steps to verify the change locally or in CI. -->

```bash
# Example
docker compose -f infra/docker/docker-compose.core.yml up -d
curl http://localhost:8000/healthz
```

## Checklist

- [ ] Code follows the existing patterns and naming conventions
- [ ] `ruff check` passes
- [ ] `ruff format --check` passes
- [ ] Tests added or updated (if applicable)
- [ ] Documentation updated (if applicable)
- [ ] Docker Compose / Helm updated (if new service or config)
- [ ] NATS subjects documented (if new events)
- [ ] `tenant_id` handled correctly for multi-tenancy
