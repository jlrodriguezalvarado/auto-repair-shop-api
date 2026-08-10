# Auto Repair Shop API

Multi-tenant SaaS API for auto repair shop management. Built with **Django 5**, **Django REST Framework**, and **PostgreSQL**.

Companion frontend: [auto-repair-shop-front](https://github.com/jlrodriguezalvarado/auto-repair-shop-front)

## Why this project

Portfolio / production-shaped backend that shows how I structure real features end to end:

- Tenant isolation by `company` with role-based access (`SUPER_ADMIN`, Admin, Secretary, Mechanic, Customer)
- JWT auth, OpenAPI (Swagger / ReDoc), soft-delete patterns
- Domain modules: customers, vehicles, service catalog, work orders, estimates (PDF), receipts & partial payments, dashboard
- Docker local workflow + production image / Compose deploy under Traefik
- Agent-assisted delivery kit (`.agents/`, dated plans, QA gate) documenting how work is planned and verified

## Stack

| Layer | Choice |
|-------|--------|
| Runtime | Python 3.12, Django 5, DRF, SimpleJWT |
| DB | PostgreSQL 16 |
| Docs | drf-spectacular |
| PDF | ReportLab |
| Deploy | Docker, Gunicorn, optional S3 media, Web Push (VAPID) |

## Quick start (local)

Requires Docker and a shared Postgres on network `dev-tools` (see `docker-tools` / `DOCKER_TOOLS_DIR`).

```bash
cp --update=none .env.example .env
./start.sh
```

API default: `http://localhost:8001`

- Swagger: `/api/schema/swagger-ui/`
- ReDoc: `/api/schema/redoc/`

Seed demo data (after migrate):

```bash
docker exec -it mechanics_api_app python manage.py seed_data
```

| User | Password | Role |
|------|----------|------|
| `superadmin` | `superadmin123` | `SUPER_ADMIN` |
| `admin` | `admin123` | `ADMIN` |
| `secretary` | `sec123` | `SECRETARY` |
| `mechanic` | `mech123` | `MECHANIC` |

Seed passwords are **demo-only**. Never reuse them outside local.

## Main endpoints

- `/api/users/` — users & JWT (`/token/`, `/users/me/`, change password)
- `/api/companies/` — companies (`SUPER_ADMIN`)
- `/api/company/` — current tenant company
- `/api/customers/profiles/` — customers
- `/api/vehicles/vehicles/` — vehicles
- `/api/catalog/services/` — service catalog
- `/api/work-orders/orders/` — work orders
- `/api/estimates/estimates/` — estimates + PDF
- `/api/receipts/receipts/` — receipts & payments
- `/api/dashboard/summary/` — tenant stats

## Architecture notes

```text
apps/
  company/     tenant model
  users/       auth, roles, tenancy
  customers/ vehicles/ catalog/
  work_orders/ estimates/ receipts/
  dashboard/   selectors for summary KPIs
config/        settings (local / production)
deploy/        production Compose, backup/restore
```

Multi-tenant migrations are **breaking** for older single-tenant DBs. Prefer wipe + migrate + seed locally (see below).

```bash
docker exec -it mechanics_api_app python manage.py flush --noinput
docker exec -it mechanics_api_app python manage.py migrate --noinput
docker exec -it mechanics_api_app python manage.py seed_data
```

## Production deploy

See [DEPLOY.md](DEPLOY.md). Copy `deploy/.env.example` → server `.env` with real secrets. Never commit `.env`, PEMs, or registry credentials.

## Working style (agents & plans)

This repo includes `.agents/` policies and `.plans/` dated feature plans used with Cursor agents (`django-api`, `qa`). That kit is intentional: contracts first, then implementation, then an independent QA pass.

## License

MIT — see [LICENSE](LICENSE).

## Security

See [SECURITY.md](SECURITY.md).
