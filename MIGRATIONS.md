# Multi-tenant migration notes

## Summary

The `*_multi_tenant_company` migrations add a non-null `company` ForeignKey to
tenant-owned tables (customers, vehicles, catalog, work orders, estimates,
receipts, users) **without** a data migration that invents a company for legacy
rows.

| Install type | What to do |
|--------------|------------|
| **New database** | `migrate` then `seed_data` — OK |
| **Legacy single-tenant DB** with existing rows | Wipe + migrate + seed (or restore a backup taken after multi-tenant). Do **not** invent a company assignment |

## Why no automatic data migration

Guessing a default company for existing rows would silently attach another
tenant's data or invent ownership. That is unsafe for production and for any
shared local DB with real content.

## Local recovery (development only)

```bash
docker compose -f docker-compose.yml exec -T mechanics_api_app python manage.py flush --noinput
docker compose -f docker-compose.yml exec -T mechanics_api_app python manage.py migrate --noinput
docker compose -f docker-compose.yml exec -T mechanics_api_app python manage.py seed_data
```

If migrate fails on non-null `company` because old rows exist, flush (or drop
the DB) and re-migrate. Prefer documenting over fake `RunPython` company guesses.
