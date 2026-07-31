# Perfil, password y permisos de dispositivo

- Plan date: 2026-07-29 (America/Caracas)
- Status: completed
- Repositories: both
- Approved by: user (Cursor plan Profile password media)

## Context and outcome

Integrar cambio de contraseña, permisos de cámara/micrófono (solo front) y alinear el menú de perfil/push como en home-front, reutilizando las notificaciones ya existentes.

## Scope

### API

- Campo `tokens_invalid_before` en User + migración
- `POST /api/users/change-password/`
- `UserAwareJWTAuthentication` + `token_blacklist`
- Tests de change-password

### Frontend

- `MediaPermissionService`
- `UserProfileMenuComponent` en shell (push, camera, mic, profile, logout)
- Feature `/profile` (cuenta, device permissions, change password)
- i18n keys + endpoints

## Contracts and compatibility

- `POST /api/users/change-password/` body: `{ current_password, new_password, confirm_password }` → `{ detail }`
- Auth Bearer; errors field-keyed; tokens previos invalidados vía `tokens_invalid_before` (+ blacklist)
- Notifications/push: unchanged

## Data, tasks, caching, and security

- Migration aditiva User
- `rest_framework_simplejwt.token_blacklist`
- Front fuerza logout tras password change
- Media permissions: solo browser Permissions API / getUserMedia

## Acceptance criteria

- [x] Usuario autenticado puede cambiar password; tokens previos dejan de autenticar; front fuerza re-login
- [x] Menú de perfil: toggle push, camera/mic, link `/profile`, logout
- [x] `/profile` muestra cuenta + permisos + form password
- [x] Panel in-app del header sigue funcionando
- [x] Sin regresiones push post-login / cleanup logout

## Verification plan

- API: pytest change-password tests
- Front: build / lint targeted
- QA subagent PASS

## Risks and non-goals

- No WebSocket notifications, forgot/reset password, dark theme, ni consumidores reales de camera/mic

## Approved amendments

- None

---

## Final result

- Completion date: 2026-07-29 (America/Caracas)
- QA verdict: PASS

### Delivered

- **auto-repair-shop-api:** `tokens_invalid_before` + migración `0002`; `UserAwareJWTAuthentication`; `POST /api/users/change-password/`; `token_blacklist`; tests `apps.users.tests.test_change_password` (6 OK).
- **auto-repair-shop-front:** `MediaPermissionService`; `UserProfileMenuComponent` en shell (idioma, push, camera, mic, perfil, logout); feature `/profile` (cuenta, permisos, change password → logout); endpoints + i18n ES/EN.

### Deviations from approved plan

- None

### Verification evidence

- `docker exec mechanics_api_app python manage.py migrate --noinput` — token_blacklist + users.0002 OK
- `docker exec mechanics_api_app python manage.py test apps.users.tests.test_change_password -v2` — Ran 6 tests OK
- `npx ng build --configuration=development` — OK, chunk `profile-component`
- QA subagent — PASS ([QA](07c047ca-de56-4ae2-b315-96349a34942e))

### Migrations and contracts

- `users.0002_user_tokens_invalid_before` aplicada
- Contrato: `POST /api/users/change-password/` body snake_case → `{ detail }`
- OpenAPI spectacular `--validate` falla por bug preexistente en `EstimateViewSet.get_permissions` (AnonymousUser.role) — no introducido por este feature

### Commits

- Ninguno (no solicitado)

### Residual risks and follow-up

- Pipeline OpenAPI/types incompleto hasta endurecer `get_permissions` ante AnonymousUser
- Sin consumidores reales de camera/mic (fuera de alcance)
- Karma/ChromeHeadless no disponible en este host

### Harness improvements

```text
Harness improvement required:
Failure class: get_permissions/get_queryset assume authenticated User.role during spectacular/schema generation
Repeat risk: high
Owner repos: auto-repair-shop-api
auto-repair-shop-api must: rule/policy + harden get_permissions for AnonymousUser (estimates/work_orders/etc.) + CI spectacular --validate; path hint: apps/*/views/api.py, .agents/policies/django-api.md
auto-repair-shop-front must: none
Record in plan: Harness improvements
```

Not landed in this feature (pre-existing; residual follow-up).

### External actions

- Push: no
- Merge: no
- Deploy: no
- Production migrations: no
