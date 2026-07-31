# Borrado lógico + restauración (sistema completo)

- Plan date: 2026-07-31 (America/Caracas)
- Status: completed
- Repositories: both
- Approved by: user (alcance D + filtro en cada lista)

## Context and outcome

Hoy los `DELETE` son físicos y el front “baja” maestros con `is_active`. Se introduce soft-delete uniforme restaurable: eliminar oculta el registro; el filtro **Eliminados** + **Restaurar** lo recupera.

## Scope

### API

- `deleted_at` en BaseModel + SoftDeleteManager (`objects` / `all_objects`)
- SoftDeleteViewSetMixin: soft destroy, `POST .../restore/`, query `deleted=false|true|all`
- Uniques parciales WHERE deleted_at IS NULL
- Company soft-delete bloquea login/refresh del tenant
- Tests + OpenAPI validate

### Frontend

- Filtro Todos / Activos / Eliminados en cada lista
- Eliminar → DELETE; Restaurar → POST restore
- Repositories + tipos OpenAPI

## Contracts and compatibility

- `DELETE` → soft-delete 204; fila con `deleted_at`
- `POST /{id}/restore/` → 200 + recurso
- `GET ?deleted=false|true|all` (default false)
- Responses incluyen `deleted_at` nullable
- Expand compatible: sin `deleted` = solo no eliminados
- OpenAPI validate; frontend regenera tipos

## Data, tasks, caching, and security

- Migraciones additive + partial unique indexes (PostgreSQL)
- Sin cascade soft-delete de subtree
- Sin hard-delete en UI; sin Celery/purge

## Acceptance criteria

- [x] Todo modelo de dominio soporta soft-delete + restore vía API
- [x] List default no muestra eliminados; `deleted=true` sí; restore los reaparece
- [x] Uniques parciales permiten recrear placa/nombre/código/username tras borrar
- [x] Soft-delete de Company bloquea acceso del tenant hasta restore
- [x] Cada lista Angular tiene filtro Todos/Activos/Eliminados + Eliminar/Restaurar
- [x] OpenAPI válido; tests API; front tsc + build:prod (Karma BLOCKED sin Chrome)
- [x] QA PASS registrado en el plan

## Verification plan

API Compose: check, makemigrations --check, migrate --plan, spectacular --validate, test --keepdb.
Front: tsc app+spec, tests headless, build:prod, api:types:check si existe.

## Risks and non-goals

- Migraciones unique AbstractUser / codes requieren PostgreSQL.
- Non-goal: hard-delete UI, papelera global, purge, cascade soft-delete.

## Approved amendments

- None.

---

## Final result

- Completion date: 2026-07-31 (America/Caracas)
- QA verdict: PASS

### Delivered

- **API:** `deleted_at` en BaseModel; SoftDelete managers; SoftDeleteViewSetMixin (DELETE soft, POST restore, `?deleted=`); uniques parciales; auth bloquea user/company eliminados; login prefiere username vivo tras reuso; migraciones soft_delete; tests; OpenAPI regenerado.
- **Front:** filtro Todos/Activos/Eliminados + Eliminar/Restaurar en customers, vehicles, service-catalog, users, companies, estimates, work-orders, receipts; repos restore; mensajes login `user_deleted`/`company_deleted`.

### Deviations from approved plan

- `Notification` (read-only) y `ReceiptPayment` (sin ViewSet) no exponen restore HTTP; heredan soft-delete a nivel modelo.
- Karma no ejecutado (Chrome ausente en WSL); tsc + build:prod OK.

### Verification evidence

- `docker compose exec -T mechanics_api_app python manage.py test apps.common.tests.test_soft_delete --keepdb --noinput` — 8 OK
- `docker compose exec -T mechanics_api_app python manage.py test --keepdb --noinput` — 55 OK
- `spectacular --validate` — Errors: 0; Warnings: 2 (preexistentes)
- Front `tsc` app+spec — OK; `build:prod` — OK
- Karma — BLOCKED (sin ChromeHeadless)

### Migrations and contracts

- Migraciones `*_soft_delete.py` aplicadas en Compose.
- Contrato: DELETE soft 204; POST `.../restore/` 200; `deleted` query; `deleted_at` en responses; códigos auth `user_deleted` / `company_deleted`.

### Commits

- Ninguno (no solicitado).

### Residual risks and follow-up

- Hijos no se soft-deleten en cascade (non-goal).
- Instalar Chrome/Chromium para correr specs headless.
- OpenAPI warnings heredados (`get_totals`, enum status).

### Harness improvements

- 2026-07-31 — Auth soft-delete usaba `all_objects.filter(username).first()` y rechazaba username reciclado — fix + test; bullets en `.agents/policies/django-api.md` (prefer alive user; `apps/__init__.py` para discovery; `Meta.ordering` en modelos con constraints).

### External actions

- Push: no
- Merge: no
- Deploy: no
- Production migrations: no
