# App Taller Mecánico API

API multi-tenant (SaaS) para la gestión de talleres mecánicos, construida con Django 5 y DRF.

## Características
- Autenticación JWT.
- Multi-empresa: `SUPER_ADMIN` gestiona empresas; el negocio queda aislado por `company`.
- Roles de tenant: Admin, Secretary, Mechanic, Customer.
- Clientes, Vehículos y Catálogo de Servicios por empresa.
- Órdenes de Trabajo con snapshots de servicios e ítems.
- Presupuestos con generación de PDF y conversión a órdenes.
- Recibos con pagos parciales y generación de PDF.
- Dashboard de estadísticas por empresa.

## Endpoints Principales
- **/api/users/**: Usuarios y tokens.
- **/api/companies/**: CRUD de empresas (`SUPER_ADMIN` only).
- **/api/company/**: Mi empresa del tenant autenticado.
- **/api/customers/profiles/**: Gestión de clientes.
- **/api/vehicles/vehicles/**: Gestión de vehículos.
- **/api/catalog/services/**: Catálogo de servicios.
- **/api/work-orders/orders/**: Órdenes de trabajo.
- **/api/estimates/estimates/**: Presupuestos.
- **/api/receipts/receipts/**: Recibos y pagos.
- **/api/dashboard/summary/**: Estadísticas.

## Documentación
- Swagger UI: `/api/schema/swagger-ui/`
- ReDoc: `/api/schema/redoc/`

## Wipe + migrate + seed (local, breaking multi-tenant)

La migración multi-tenant es **breaking**. En local, recrea la BD antes de migrar:

```bash
# Desde auto-repair-shop-api (contenedor en marcha)
docker exec -it mechanics_api_app python manage.py flush --noinput
# O drop/recreate del schema en Postgres compartido, por ejemplo:
# docker exec -it tools_postgres psql -U postgres -c "DROP DATABASE IF EXISTS mechanics_api;"
# docker exec -it tools_postgres psql -U postgres -c "CREATE DATABASE mechanics_api;"

docker exec -it mechanics_api_app python manage.py migrate --noinput
docker exec -it mechanics_api_app python manage.py seed_data
```

## Credenciales seed

| Usuario | Password | Rol | Empresa |
|---------|----------|-----|---------|
| `superadmin` | `superadmin123` | `SUPER_ADMIN` | — |
| `admin` | `admin123` | `ADMIN` | Taller Mecánico Demo |
| `secretary` | `sec123` | `SECRETARY` | Taller Mecánico Demo |
| `mechanic` | `mech123` | `MECHANIC` | Taller Mecánico Demo |

```bash
docker exec -it mechanics_api_app python manage.py seed_data
```
