# Hard-delete permanente (complemento soft-delete)

- Plan date: 2026-07-31 (America/Caracas)
- Status: completed
- Repositories: both
- Approved by: user (opción 2 por default; rechazo de plan mode + “no veo eliminar permanente de companies”)

## Context and outcome

Tras soft-delete + restore, el SuperAdmin (companies) y el Admin de tenant necesitan **eliminar de forma permanente** registros ya en papelera, con confirmación explícita. Hoy no hay endpoint ni botón.

## Scope

### API

- Extender `SoftDeleteViewSetMixin` con `POST .../{id}/hard-delete/` → **204**
- Solo si `deleted_at` no es null; si está activo → **400**
- Permisos más estrictos (opción 2): **Admin** en tenant; **SuperAdmin** en companies
- Company: antes del hard-delete físico, `User.all_objects.filter(company=...).hard_delete()` (FK `PROTECT`)
- Tests + OpenAPI regenerado

### Frontend

- En filas con `deletedAt`: botón **Eliminar permanente** junto a Restaurar (companies + listas tenant con soft-delete)
- Confirmación: “esta acción no se puede deshacer”
- Repos: `hardDelete(id)` → `POST .../hard-delete/`
- Companies: visible para SuperAdmin; tenant: solo Admin (`hasRole(['ADMIN'])`) + `canMutateTenantData()`

## Contracts and compatibility

- `POST /api/.../{id}/hard-delete/` → 204 No Content
- 400 si el registro no está soft-deleted
- 403 sin permiso
- OpenAPI: acción documentada; front regenera tipos si aplica / endpoints manuales

## Acceptance criteria

- [ ] Soft-deleted company: SuperAdmin ve Restaurar + Eliminar permanente; hard-delete la quita de `deleted=true` y de DB
- [ ] Company activa: hard-delete API → 400
- [ ] Tenant Admin: mismo patrón en customers/vehicles/catalog/users/estimates/work-orders/receipts
- [ ] Secretary: no ve / no puede hard-delete
- [ ] Confirmación irreversible en UI

## Verification plan

- API: tests soft_delete + hard_delete company/customer
- Front: build / smoke listas Eliminados
- QA subagent al integrar

## Risks and non-goals

- Hard-delete de Company borra usuarios del tenant y cascada CASCADE del resto
- No cascade soft-delete; no hard-delete desde registros activos
- No papelera global

## Approved amendments

- 2026-07-31 — Permisos opción **2** (Admin / SuperAdmin companies). Botón solo en eliminados.

---

## Final result

- Completion date: 2026-07-31 (America/Caracas)
- QA verdict: PASS (tras reinicio API + fix OpenAPI 204; smoke vivo OK)

### Delivered

- **API:** `POST .../{id}/hard-delete/` → 204; 400 si vivo; Admin tenant / SuperAdmin companies; Company hard-delete borra users (PROTECT) en transacción; tests soft_delete 11 OK; OpenAPI con `extend_schema(request=None, responses={204: None})`.
- **Front:** botón `delete_forever` junto a Restaurar en companies + listas tenant (solo Admin); confirmación irreversible; repos/endpoints.

### Deviations from approved plan

- None.

### Verification evidence

- `manage.py test apps.common.tests.test_soft_delete --keepdb` — 11 OK
- `spectacular --validate` — Errors: 0
- Smoke: alive company hard-delete → 400; soft+hard company → 204; GET after → 404
- Front: `tsc` + `build:prod` OK (angular-frontend)

### Migrations and contracts

- Sin migraciones nuevas.
- Contrato: `POST /hard-delete/` 204 sin body.

### Commits

- (no commits — no solicitados)

### Residual risks and follow-up

- Gunicorn sin reload: reiniciar `mechanics_api_app` tras cambios de código en local.
- Nested line-item ViewSets también exponen hard-delete vía mixin (sin UI).

### Harness improvements

- 2026-07-31 — Failure class: void `@action` POST published as 200 + required serializer body — landed in `auto-repair-shop-api/.agents/policies/django-api.md` (bullet `extend_schema(request=None, responses={204: None})`) + decorator on `SoftDeleteViewSetMixin.hard_delete`.

### External actions

- Push: no
- Merge: no
- Deploy: no
- Production migrations: no

