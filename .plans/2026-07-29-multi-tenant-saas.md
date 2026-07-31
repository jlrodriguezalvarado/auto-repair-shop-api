# Multi-tenant SaaS por empresa

- Plan date: 2026-07-29 (America/Caracas)
- Status: completed
- Repositories: both
- Approved by: user (explicit implement request)

## Context and outcome

Convertir el sistema de single-tenant a SaaS multi-empresa: Super Admin gestiona empresas; todo el negocio (usuarios, clientes, vehículos, catálogo, OT, presupuestos, recibos) queda aislado por `company_id`. Se recrea la BD y el seed con datos demo.

## Scope

### API

- Rol `SUPER_ADMIN` (company null); usuarios de tenant con FK `company` obligatoria.
- FK `company` en CustomerProfile, Vehicle, ServiceCatalog, WorkOrder, Estimate, Receipt.
- Uniques por tenant: plate, service name.
- Endpoints `/companies/` (SUPER_ADMIN CRUD + admin inicial) y `/company/` (mi empresa del tenant).
- Filtrado queryset por company; SUPER_ADMIN 403 en endpoints de negocio.
- Wipe BD + seed: superadmin + empresa demo + admin/secretaria/mecánico + catálogo.
- Tests de aislamiento + OpenAPI.

### Frontend

- Feature Companies (SUPER_ADMIN).
- Mi empresa para ADMIN/SECRETARY del tenant.
- Nav/guards por rol; User.company en tipos; mocks alineados.

## Contracts and compatibility

- Breaking change aceptado (wipe + seed).
- Auth/user payload incluye `company` (`id` + `name` o null).
- OpenAPI regenerado; front corre `npm run api:types` si aplica.

## Data, tasks, caching, and security

- Migraciones con wipe de BD local.
- Aislamiento forzado en API (mixin/helper de tenant).
- Sin billing, subdominios ni impersonación.

## Acceptance criteria

- [x] Solo `SUPER_ADMIN` lista/crea/edita/borra empresas.
- [x] Al crear empresa se crea el ADMIN inicial de ese tenant.
- [x] Admin/secretaria/mecánico/cliente solo ven datos de su empresa.
- [x] Catálogo es por empresa.
- [x] `/company/` edita solo la empresa del usuario autenticado.
- [x] Seed documentado: superadmin + empresa demo + admin/secretaria/mecánico.
- [x] QA cross-layer PASS.

## Verification plan

- API: migraciones, seed, tests tenant, OpenAPI.
- Front: build + flujos Super Admin vs Admin tenant.
- Subagente `qa`.

## Risks and non-goals

- Riesgo: queryset sin filtro = fuga → mixin obligatorio.
- Non-goals: billing, subdominios, impersonación, multi-company users, Super Admin operando OT de tenants.

## Approved amendments

- None.

---

## Final result

- Completion date: 2026-07-29 (America/Caracas)
- QA verdict: PASS

### Delivered

- **API:** SUPER_ADMIN, FK `company` en modelos de negocio, `/api/companies/` + `/api/company/`, mixin de aislamiento, seed, tests (27 OK), OpenAPI.
- **Front:** feature Companies (SUPER_ADMIN), Mi empresa (tenant), nav/guards/login redirect, tipos y mocks.

### Deviations from approved plan

- UI Companies: list/create/edit sin botón delete (API sí expone DELETE). No bloqueante.

### Verification evidence

- `manage.py check` — 0 issues
- `spectacular --validate` — 0 errors (2 warnings previos)
- `test apps.company.tests.test_tenancy + work_orders + change_password` — 27 OK
- `ng build` development + production — OK
- Live smoke: SUPER_ADMIN POST companies 201; tenant 403 on `/companies/`; isolation tests PASS

### Migrations and contracts

- Migraciones additive `*_multi_tenant_company.py`; BD flush + migrate + seed aplicados en entorno local.
- Create company: `admin_user` nested; user payload `company: {id, name} | null`.
- Wipe (otros entornos):
  ```bash
  docker exec -it mechanics_api_app python manage.py flush --noinput
  docker exec -it mechanics_api_app python manage.py migrate --noinput
  docker exec -it mechanics_api_app python manage.py seed_data
  ```

### Commits

- None (not requested).

### Residual risks and follow-up

- OpenAPI `User.company` sin `nullable: true` (runtime envía null para SUPER_ADMIN).
- SECRETARY puede intentar guardar Mi empresa; API responde 403 (solo ADMIN escribe).
- ChromeHeadless specs no ejecutados (sin browser en entorno).

### Harness improvements

- None.

### External actions

- Push: no
- Merge: no
- Deploy: no
- Production migrations: no
