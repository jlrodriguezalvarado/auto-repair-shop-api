# Django API engineering policy

Keep aligned with sibling awareness in `../auto-repair-shop-front/.agents/policies/integration.md`.

Companion policies: `integration.md` (Angular consumer) and `qa.md` (final gate).

## Architecture and contracts

- Stack: Django, Django REST Framework, drf-spectacular, PostgreSQL (prefer over SQLite for Docker/local parity).
- First-party consumer: Angular app in sibling `auto-repair-shop-front`. Design every HTTP change for that client: stable field names, documented OpenAPI, trailing-slash canonical routes, and lossless decimals.
- Keep domain logic in services and complex/read-optimized queries in selectors when that separation has real value. Keep simple CRUD direct and readable.
- Use explicit request/response serializers. Maintain the standard error envelope: `code`, `message`, `field_errors`, `details`, and `request_id`, retaining required legacy keys.
- Keep canonical trailing-slash routes and compatibility aliases until their removal is explicitly planned.
- User-owned resources must be scoped before lookup; never fetch globally and check ownership afterward when the queryset can enforce it.
- Preserve decimal values losslessly at the HTTP boundary. Prefer UUID identifiers and database constraints consistent with the existing domain.
- After schema changes, validate OpenAPI (`manage.py spectacular --validate`) and tell the orchestrator to adapt `auto-repair-shop-front` (regenerate types when that pipeline exists).
- Void custom `@action` POSTs (e.g. hard-delete): decorate with `@extend_schema(request=None, responses={204: None})` (or the real status) so spectacular does not invent a required serializer body and `200` + model schema. After regenerating `docs/openapi.yaml`, assert the operation has no required requestBody and documents the intended empty success status.
- Soft-delete auth: when looking up a user by unique field that can be recycled after soft-delete (e.g. username), prefer the alive row (`objects` / `deleted_at IS NULL`) before treating a soft-deleted row as the login subject. Cover with a regression test (soft-delete → recreate same username → login succeeds).
- Keep `apps/` as a real Python package (`apps/__init__.py`) so `manage.py test` discovers tests under `apps.*`.
- Concrete model `Meta` that declares `constraints` must also set `ordering` explicitly if list pagination should stay ordered (abstract `BaseModel.Meta.ordering` is not inherited when the child defines its own `Meta`).

## PostgreSQL and migrations

- Develop and test against PostgreSQL behavior, not SQLite assumptions.
- Prefer additive expand-contract migrations. No destructive migration or production migration without explicit authorization.
- Run `makemigrations --check --dry-run`; inspect every migration and `migrate --plan`.
- Add indexes only for demonstrated access patterns. Prevent N+1 with `select_related`, `prefetch_related`, annotations, or batch selectors; add query-count tests only where regression risk is concrete.
- Keep transactions short. Never hold a database transaction open across an external API call.

## Background work

- This API does not ship Celery/Redis yet. Prefer synchronous request handling or introduce a queue only with an approved plan.
- If background jobs are added later, queue them with `transaction.on_commit` and document the worker topology in deploy docs.

## Security and observability

- Never weaken production settings, secrets validation, host/CORS checks, secure cookies, health semantics, or request-ID propagation.
- Do not expose exception strings, credentials, internal connection details, or private objects in responses or logs.
- Liveness has no dependencies; readiness checks required dependencies without leaking configuration.

## Verification

Use the running Compose service when available:

```bash
docker compose exec -T mechanics_api_app python manage.py check
docker compose exec -T mechanics_api_app python manage.py makemigrations --check --dry-run
docker compose exec -T mechanics_api_app python manage.py migrate --plan
docker compose exec -T mechanics_api_app python manage.py spectacular --validate --file /tmp/openapi-validation.yaml
docker compose exec -T mechanics_api_app python manage.py test <affected.apps> --keepdb --noinput
```

Before final QA, the global PostgreSQL suite must pass:

```bash
docker compose exec -T mechanics_api_app python manage.py test --keepdb --noinput
```
