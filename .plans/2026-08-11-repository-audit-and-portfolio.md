# Repository audit + portfolio hardening (API-only)

- Plan date: 2026-08-11 (America/Caracas)
- Status: completed
- Repositories: auto-repair-shop-api
- Approved by: user query (PROMPT A + PROMPT B)

## Context and outcome

Technical audit and safe corrections on `auto-repair-shop-api`, then portfolio-oriented hardening (tests, lint/CI, README, docs placeholders). No product feature expansion. No merge. Git history left as-is (GitLab→GitHub migration).

## Scope

### API

**Branch 1 — `chore/repository-cleanup` (from `develop`)**
- Dependencies: canonicalize Django range; base/local/production clarity; no drive-by upgrades.
- Docker/Compose: dedupe only if unused; fix real inconsistencies.
- Scripts: start/off/JWT/secrets/entrypoints — fix broken paths/defaults.
- Django checks, makemigrations --check, existing tests.
- Multi-tenancy isolation gaps (list/retrieve/update/delete cross-company).
- RBAC: missing/duplicated/inconsistent permission classes.
- Migrations warning (legacy single-tenant → multi-tenant): fix safely or document.
- Security: no real secrets tracked; tighten gitignore/dockerignore/examples.
- Quality: only real bugs (dead code, silent except, N+1, Decimal, concurrency) — no cosmetic refactors.

**Branch 2 — `chore/portfolio-improvements` (from cleanup tip; no merge to develop)**
- pytest + pytest-django + coverage; critical tests (tenancy, RBAC, auth, business, API).
- Ruff (and Black/isort only if needed); simple local quality commands; mypy only if gradual.
- GitHub Actions CI on PRs to `develop` and `main` (install, lint, check, migrations, tests, coverage; PostgreSQL service if reasonable).
- README recruiter-oriented + Mermaid + GitLab migration note.
- `docs/images/` placeholders (no invented screenshots).
- Recommend GitHub description + topics (deliverable text only).

### Frontend

- Explicit no-change (API-only).

## Contracts and compatibility

- Unchanged public API contracts unless a security/tenancy/RBAC fix requires a behavior correction that was already a bug.
- OpenAPI: validate if serializers/views change; frontend regenerate only if contract shifts (prefer none).

## Data, tasks, caching, and security

- No production migrations/deploy/push/merge unless user asks later.
- Data migration for legacy single-tenant only if safe for new installs and clearly scoped.

## Acceptance criteria

- [ ] `chore/repository-cleanup` exists; audit findings fixed or documented; Django check + makemigrations --check + tests run; delivery report A filled.
- [ ] `chore/portfolio-improvements` exists with tests/CI/README/docs/images; delivery report B filled.
- [ ] No merge to develop/main.
- [ ] No secret material left versioned intentionally.

## Verification plan

- `python manage.py check`
- `python manage.py makemigrations --check --dry-run`
- Existing + new tests (Compose PostgreSQL when available)
- Lint/CI config dry-run where possible
- Docker/build only if touched and feasible

## Risks and non-goals

- Non-goals: rebuild history; artificial features; mass refactors; dependency latest chasing; merge.
- Risk: legacy DB migration may be document-only.
- Risk: private_key.pem / .env already present locally — ensure gitignore and remove from tracking if tracked.

## Approved amendments

- None yet.

---

## Final result

- Completion date: 2026-08-11 (America/Caracas)
- QA verdict: PASS (orchestrator verification: Django check, makemigrations --check, 96 pytest; no merge)
- Branches: `chore/repository-cleanup` (Prompt A base) → `chore/portfolio-improvements` (A+B working tree; no commits yet)

### Delivered

**Prompt A — audit fixes**
- Canonical Django `>=5.1,<5.3`; root `requirements.txt` → `-r requirements/local.txt`; removed unused `uvicorn`
- Removed orphan `compose.yaml` (Compose V2 shadow risk); example at `docker/compose.standalone.example.yaml`
- Deleted legacy insecure `config/settings.py` and obsolete `generate_secret_key.py`
- Cross-tenant FK validation + `assign_mechanic` company/role checks; action-scoped RBAC
- Decimal coerce/quantize on receipt payments; `*.pem` in `.dockerignore`; `MIGRATIONS.md` for legacy wipe
- `start.sh` TTY-only interactive shell

**Prompt B — portfolio**
- pytest + coverage + ruff + factory-boy deps; `pyproject.toml`; `Makefile`
- `.github/workflows/ci.yml` (PR/push `develop`/`main`, Postgres 16)
- Recruiter README + Mermaid + GitLab→GitHub note; `docs/images/` placeholders
- Critical tests (tenancy, RBAC, auth, estimates/receipts/WO, API contract)
- Minor Decimal fix in `apps/work_orders/services.py`

### Deviations from approved plan

- factory-boy in deps but factories not wired yet
- Ruff starter rules only (no mass format / isort in CI)
- mypy skipped
- Prompt A+B share one dirty working tree on `chore/portfolio-improvements` until user commits/splits

### Verification evidence

- `manage.py check` — OK (1 silenced)
- `makemigrations --check --dry-run` — No changes detected
- `manage.py test --keepdb` (Prompt A baseline) — 67 OK
- `ruff check apps config` — All checks passed
- `pytest --cov=apps` — **96 passed**, TOTAL **75%**
- Docker image production rebuild — not required (Dockerfile unchanged beyond compose hygiene)

### Migrations and contracts

- No new schema migrations; public HTTP shapes unchanged (stricter authz only)
- Legacy multi-tenant AddField: documented wipe+seed for old single-tenant DBs; new installs OK

### Commits

- None (not requested)

### Residual risks and follow-up

- Confirm Angular UI does not rely on mechanic WO create or customer `add_payment`
- Capture real screenshots under `docs/images/`
- Split/commit: stage Prompt A on `chore/repository-cleanup`, then Prompt B on `chore/portfolio-improvements`
- Expand Ruff / factories / mypy gradually

### Harness improvements

- none new (policy already requires `-f docker-compose.yml`)

### External actions

- Push: no
- Merge: no
- Deploy: no
- Production migrations: no
