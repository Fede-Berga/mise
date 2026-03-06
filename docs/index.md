# Mise Platform Documentation

Mise is a multi-tenant restaurant operations platform built around clear service boundaries, event-driven workflows, and role-based access control.

This documentation focuses on operating and validating the current MVP with professional engineering hygiene.

## What You Can Do Here

- Run the platform locally with Docker Compose.
- Test role-based workflows (`owner`, `manager`, `chef`, `waiter`, `cashier`).
- Validate order-to-kitchen lifecycle consistency.
- Use structured QA checklists before release tagging.

## Recommended Reading Order

1. [Quickstart (Docker Core)](getting-started/quickstart.md)
2. [Test Users & Roles](getting-started/roles.md)
3. [Manual E2E Checklist](qa/e2e-checklist.md)
4. [Test Strategy](qa/test-strategy.md)

## Documentation Stack

This docs site is built with:

- [MkDocs](https://www.mkdocs.org/) (open source, BSD license)
- [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) (open source, MIT license)

Both tools are free and open source.
