# Cross-layer integration policy

Keep aligned with `../auto-repair-shop-front/.agents/policies/integration.md`.

This product pairs two repositories:

| Layer | Path | Role |
|-------|------|------|
| Django API | this repo (`auto-repair-shop-api`) | Source of truth for persistence, auth, business rules, OpenAPI |
| Angular app | sibling `../auto-repair-shop-front` | Sole first-party HTTP/WebSocket consumer of that API |

## Contract ownership

- Django owns transport contracts: routes, serializers, pagination, error envelope, auth headers/cookies, decimal encoding, and `docs/openapi.yaml`.
- Angular owns presentation and client-side domain models. It maps DTOs into feature models and must not redefine server rules in the UI.
- When a feature needs a new field or endpoint, change the API contract first (compatible expand), validate OpenAPI, regenerate Angular types, then adapt repositories/mappers/UI.

## Low-friction defaults

- Canonical trailing-slash routes in Angular; Django keeps legacy aliases until an approved removal phase.
- Uniform error envelope (`code`, `message`, `field_errors`, `details`, `request_id`) with required legacy keys retained.
- Pagination: support modern page payloads and legacy arrays via shared frontend helpers; keep `perPage` compatible while capped server-side.
- Money/decimals: JSON strings end-to-end until deliberate decimal arithmetic in the client.
- Auth: JWT refresh shared across concurrent 401s; final failure clears user-scoped client state.
- Types: `auto-repair-shop-front` uses `npm run api:types` / `api:types:check` against `auto-repair-shop-api/docs/openapi.yaml`; repositories remain manual and typed.

## Pattern continuity

Before adding a feature, mirror an existing neighboring feature in the same domain (models/serializers/views on API; DTO/mapper/repository/component on Angular). Prefer extending established folders over inventing a new layering style.

## Explicit non-goals unless planned

- Do not remove legacy routes or response keys without an approved phase.
- Do not introduce NgRx, extra BFF services, or alternate API clients without approval.
- Do not cache authenticated API data in the Angular service worker without a reviewed policy.
