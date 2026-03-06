# Manual E2E Checklist (MVP Release)

Use this checklist before tagging an MVP release.

## Environment and Health

- [ ] `make up-core` completes without container failures.
- [ ] `restaurant/menu/order/kitchen` return healthy `/healthz`.
- [ ] Web app reachable on `http://localhost:3000`.

## Authentication

- [ ] Login succeeds via Keycloak.
- [ ] Session remains valid for at least 10 minutes while using cockpit.
- [ ] No recurring `401` on `/api/orders` or `/api/kitchen/tickets`.

## Roles and Access Control

- [ ] Owner can access dashboard/menu/orders/kitchen.
- [ ] Manager can access dashboard/menu/orders/kitchen.
- [ ] Chef only accesses kitchen.
- [ ] Waiter only accesses orders.
- [ ] Cashier only accesses orders.

## Order and Kitchen Flow

- [ ] Create order from Orders UI.
- [ ] Kitchen ticket is auto-created.
- [ ] Advance in Kitchen updates status in Orders.
- [ ] Advance in Orders updates status in Kitchen.
- [ ] `CLOSED` order maps to `DONE` kitchen ticket.

## Tenant and Restaurant Context

- [ ] Switching active restaurant changes API data scope.
- [ ] No cross-restaurant data leakage.

## Resilience

- [ ] Stop `kitchen-svc`, create order, start `kitchen-svc`.
- [ ] Ticket is eventually created after consumer restart.
- [ ] No event loss observed in logs.
