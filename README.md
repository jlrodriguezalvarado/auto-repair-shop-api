# App Taller Mecánico API

API para la gestión de un taller mecánico construida con Django 5 y DRF.

## Características
- Autenticación JWT.
- Gestión de Usuarios y Roles (Admin, Secretary, Mechanic, Customer).
- Empresa, Clientes y Vehículos.
- Catálogo de Servicios.
- Órdenes de Trabajo con snapshots de servicios e ítems.
- Presupuestos con generación de PDF y conversión a órdenes.
- Recibos con pagos parciales y generación de PDF.
- Dashboard de estadísticas.

## Endpoints Principales
- **/api/users/**: Usuarios y tokens.
- **/api/company/**: Datos de la empresa.
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
