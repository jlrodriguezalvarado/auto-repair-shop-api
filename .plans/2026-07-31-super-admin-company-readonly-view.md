# SUPER_ADMIN read-only company context (X-Company-Id)

- Plan date: 2026-07-31 (America/Caracas)
- Status: completed
- Repositories: both
- Approved by: user

## Context and outcome

SUPER_ADMIN must inspect a single company's business data without impersonating a tenant user or changing role. They stay SUPER_ADMIN and pass `X-Company-Id` on SAFE methods only; writes remain forbidden. Read visibility matches ADMIN for the selected company.

## Scope

### API

- Rewrite `apps/common/tenancy.py` with header parse, resolve, and `require_tenant_access`.
- Update `IsTenantUser` / `IsAdministrator` for SUPER_ADMIN company viewers (SAFE only).
- Scope list/detail querysets via `resolve_company_id`; keep writes on `require_tenant_user`.
- MyCompany GET via resolved company id; PUT/PATCH still tenant ADMIN via `get_user_company`.
- Document `X-Company-Id` in OpenAPI (`APPEND_COMPONENTS` + Dashboard/MyCompany parameters).
- Tests in `apps/company/tests/test_tenancy.py` (`SuperAdminCompanyViewerTests`).

### Frontend

- Send `X-Company-Id` when SUPER_ADMIN browses a company (read-only UI).
- Regenerate OpenAPI types if the pipeline consumes the new header component.
- Do not allow write actions while in company-view mode.

## Contracts and compatibility

- Header: `X-Company-Id` (integer company PK), required for SUPER_ADMIN on tenant business GET/HEAD/OPTIONS.
- Missing/invalid/non-existent company → 403.
- SAFE methods only for SUPER_ADMIN; POST/PUT/PATCH/DELETE → 403.
- No role change / no impersonation token.
- Tenant users unchanged (no header needed).
- OpenAPI: optional header component `CompanyContextHeader`; frontend should regenerate types.

## Data, tasks, caching, and security

- No migrations.
- Company existence checked before scoping.
- Writes never stamp or mutate under SUPER_ADMIN.

## Acceptance criteria

- [x] SUPER_ADMIN without header → 403 on business GETs (unchanged).
- [x] SUPER_ADMIN with `HTTP_X_COMPANY_ID` of company A → 200 on customers, vehicles, catalog, work-orders, estimates, receipts, dashboard, users, company; data scoped to A only.
- [x] Invalid / non-integer header → 403.
- [x] SUPER_ADMIN POST customer / PATCH company → 403 even with header.
- [x] Tenant ADMIN still works without header.

## Verification plan

- `docker compose exec -T mechanics_api_app python manage.py test apps.company.tests.test_tenancy --keepdb --noinput`
- `docker compose exec -T mechanics_api_app python manage.py spectacular --validate --file /tmp/openapi-validation.yaml`

## Risks and non-goals

- No SUPER_ADMIN write paths on tenant data.
- No session/role impersonation.
- No change to `/api/companies/` SUPER_ADMIN CRUD.

## Approved amendments

- None yet.

---

## Final result

- Completion date: 2026-07-31 (America/Caracas)
- QA verdict: **PASS**

### Delivered

- API: `apps/common/tenancy.py` (parse/resolve/`require_tenant_access`), `IsTenantUser`/`IsAdministrator` company-viewer SAFE path, queryset scoping via `resolve_company_id`, MyCompany GET via resolved id, OpenAPI `CompanyContextHeader` + Dashboard/MyCompany params, `SuperAdminCompanyViewerTests`.
- Frontend: `AuthService.viewingCompany` / `enterCompanyView` / `exitCompanyView` / `canMutateTenantData`; jwt interceptor sends `X-Company-Id`; roleGuard + shell ADMIN menu + banner; companies “Ver taller”; mutation UI gated; mock interceptor mirrors write 403.

### Acceptance criteria evidence

| Criterion | Result |
|-----------|--------|
| SUPER_ADMIN without header → 403 on business GETs | PASS — `test_superadmin_forbidden_on_business_endpoints` |
| SUPER_ADMIN + `X-Company-Id` A → 200 scoped reads (customers…company) | PASS — `test_superadmin_with_company_header_reads_company_a` + scoped customers |
| Invalid / non-integer header → 403 | PASS — invalid + non-integer tests |
| SUPER_ADMIN POST customer / PATCH company → 403 with header | PASS — post/patch tests |
| Tenant ADMIN without header unchanged | PASS — `test_tenant_admin_still_works_without_header` + isolation suite |
| Front: select company → ADMIN-like menu/data (GET + header) | PASS — review shell/auth/jwt |
| Front: mutations blocked + exit to companies | PASS — `canMutateTenantData` + `exitCompanyView` |

### Deviations from approved plan

- None material. Child ViewSets also call `require_tenant_user` on writes (defense in depth).
- `docs/openapi.yaml` on disk is stale (no `X-Company-Id`); live spectacular schema has `CompanyContextHeader` (validated). Front has no `api:types` script in `package.json` (header wired manually).

### Verification evidence

API (docker `mechanics_api_app`):
- `python manage.py check` — OK (0 issues)
- `python manage.py test apps.company.tests.test_tenancy --keepdb --noinput` — Ran 38, OK
- `python manage.py test apps.company.tests.test_tenancy apps.users.tests.test_change_password apps.work_orders.tests --keepdb --noinput` — Ran 47, OK (full discoverable suite; bare `manage.py test` finds 0 due to package layout)
- `python manage.py spectacular --validate --file /tmp/openapi-validation.yaml` — Errors: 0; Warnings: 2 (pre-existing)

Front:
- `npx tsc -p tsconfig.app.json --noEmit` — OK
- `npx tsc -p tsconfig.spec.json --noEmit` — OK
- `npm run build:prod` — OK
- `npm test` / ChromeHeadless — environment limitation (no Chrome binary); not a feature FAIL

### Migrations and contracts

- No migrations.
- Runtime OpenAPI documents optional `X-Company-Id`. Recommend regenerating committed `docs/openapi.yaml` as follow-up (non-blocking).

### Commits

- (none yet)

### Residual risks and follow-up

- Stale `docs/openapi.yaml` still describes SUPER_ADMIN deny-only on some tenant GETs.
- While in company-view mode, `/companies` remains reachable and company CRUD UI is unchanged (tenant mutations stay blocked; API companies CRUD ignores header).
- JWT interceptor attaches `X-Company-Id` on all authenticated calls while viewing (including writes); API correctly 403s writes.
- No Chrome in CI/agent env → unit specs not executed this gate.

### Files reviewed (high-risk)

- API: `apps/common/tenancy.py`, `apps/users/permissions.py`, `apps/company/views/api.py`, `apps/dashboard/views/api.py`, customers/vehicles/catalog/work_orders/estimates/receipts/users views, `apps/company/tests/test_tenancy.py`, `config/settings/base.py` SPECTACULAR_SETTINGS
- Front: `auth.service.ts`, `jwt.interceptor.ts`, `shell.component.{ts,html}`, `companies.component.ts`, feature templates using `canMutateTenantData`, `mock-api.interceptor.ts`, `app.routes.ts`, `i18n.service.ts`

### Harness improvements

- None required for this feature. Optional: add a check that committed `docs/openapi.yaml` is regenerated when spectacular components change (owner: `auto-repair-shop-api`).

### External actions

- Push: no
- Merge: no
- Deploy: no
- Production migrations: no
