# Deploy — auto-repair-shop-api (Traefik + private registry)

Publishes **mechanics/api** and the Compose stack that also serves **mechanics/web**
behind a reverse proxy (Traefik, Let's Encrypt, private registry).

| Component | Image | Host |
|---|---|---|
| API | `registry.example.com/mechanics/api:<git-sha>` | `mechanicsapi.example.com` |
| Front | `registry.example.com/mechanics/web:<git-sha>` | `mechanics.example.com` |

## Local vs production

| | Local | Production |
|---|---|---|
| Where | `docker-compose.yml` + shared `docker-tools` | `deploy/compose.production.yml` on `/opt/apps/mechanics` |
| API image | `django-runtime` + bind-mount | `mechanics/api:${APP_VERSION}` |
| Front | `npm start` in `auto-repair-shop-front` | `dist`-only image |
| DB | shared Postgres (`tools_postgres`) | `db` service in the stack |

## Flow

From the workspace root `mechanics/`:

```bash
./build-api.sh
./build-front.sh
./upload.sh          # or ./upload.sh all the first time
```

On the server:

```bash
cd /opt/apps/mechanics
./deploy.sh
```

## Server layout

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

API CORS must allow the front origin. Do not use the production Compose file for local development.

## Web Push (VAPID)

1. Generate keys (local machine, with `pywebpush`):

```bash
vapid --gen
vapid --applicationServerKey -k private_key.pem
```

2. On the server:

```bash
sudo install -m 600 private_key.pem /opt/apps/mechanics/secrets/vapid_private.pem
```

3. In `/opt/apps/mechanics/.env`:

```bash
WEB_PUSH_VAPID_PUBLIC_KEY=<public key from applicationServerKey>
WEB_PUSH_VAPID_PRIVATE_KEY_FILE=/run/secrets/vapid_private.pem
WEB_PUSH_VAPID_SUBJECT=mailto:admin@example.com
```

Compose mounts `./secrets:/run/secrets:ro`. Without the PEM, push delivery is skipped (warning in logs).
