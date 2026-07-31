# Deploy — auto-repair-shop-api (Traefik + registry privado)

Publica **mechanics/api** y el Compose que también sirve **mechanics/web** sobre
`secure-docker-infrastructure` (Traefik, Let's Encrypt, registry privado).

| Componente | Imagen | Host |
|---|---|---|
| API | `registry.lumuscore.com/mechanics/api:<git-sha>` | `mechanicsapi.lumuscore.com` |
| Front | `registry.lumuscore.com/mechanics/web:<git-sha>` | `mechanics.lumuscore.com` |

## Local vs producción

| | Local | Producción |
|---|---|---|
| Dónde | `docker-compose.yml` + `docker-tools` | `deploy/compose.production.yml` en `/opt/apps/mechanics` |
| Imagen API | `django-runtime` + bind-mount | `mechanics/api:${APP_VERSION}` |
| Front | `npm start` en `auto-repair-shop-front` | imagen solo-`dist` |
| DB | `tools_postgres` | servicio `db` del stack |

## Flujo

Desde la raíz del workspace `mechanics/`:

```bash
./build-api.sh
./build-front.sh
./upload.sh          # o ./upload.sh all la primera vez
```

En el servidor:

```bash
cd /opt/apps/mechanics
./deploy.sh
```

## Layout servidor

```text
/opt/apps/mechanics/
  compose.production.yml
  deploy.sh
  backup.sh
  restore.sh
  .env
  .env.deploy
  secrets/
```

CORS del API debe permitir el origen del front. No uses el Compose de producción para desarrollo local.

## Web Push (VAPID)

1. Generar claves (máquina local, con `pywebpush`):

```bash
vapid --gen
vapid --applicationServerKey -k private_key.pem
```

2. En el servidor:

```bash
sudo install -m 600 private_key.pem /opt/apps/mechanics/secrets/vapid_private.pem
```

3. En `/opt/apps/mechanics/.env`:

```bash
WEB_PUSH_VAPID_PUBLIC_KEY=<public key from applicationServerKey>
WEB_PUSH_VAPID_PRIVATE_KEY_FILE=/run/secrets/vapid_private.pem
WEB_PUSH_VAPID_SUBJECT=mailto:admin@example.com
```

Compose monta `./secrets:/run/secrets:ro`. Sin el PEM, el envío push se omite (log warning).
