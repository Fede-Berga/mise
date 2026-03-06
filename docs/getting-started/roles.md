# Test Users and Roles

This MVP supports the following roles in JWT claims:

- `owner`
- `manager`
- `chef`
- `waiter`
- `cashier`

## Role Access Matrix

| Role | Default Route | Allowed Areas |
|---|---|---|
| owner | `/dashboard` | dashboard, menu, orders, kitchen |
| manager | `/dashboard` | dashboard, menu, orders, kitchen |
| chef | `/kitchen` | kitchen |
| waiter | `/orders` | orders |
| cashier | `/orders` | orders |

## Keycloak Configuration Notes

- Roles can be assigned as realm roles or client roles (`mise-web`).
- Role extraction accepts both `realm_access.roles` and `resource_access.<client>.roles`.
- Re-login after role changes so a new token is issued.

## Restaurant/Tenant Context

- Active restaurant is selected through the UI switcher (owners with multiple restaurants).
- API tenant routing uses active restaurant context with secure server-side forwarding.
