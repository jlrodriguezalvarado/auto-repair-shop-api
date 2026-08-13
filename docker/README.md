# Docker notes (local)

- **Canonical local Compose:** `docker-compose.yml` + shared `docker-tools` via `./start.sh`.
  Prefer: `docker compose -f docker-compose.yml …`
- **Standalone example (legacy):** `docker/compose.standalone.example.yaml` — incomplete
  vs current entrypoint; align `DB_*` / `RUN_MIGRATIONS=1` before use. Kept so a root
  `compose.yaml` cannot shadow `docker-compose.yml` under Compose V2 defaults.
- **Entrypoint SoT:** `docker/entrypoint-app.sh` (used by `Dockerfile` and local Compose).
- **Historical / unused by current Dockerfile:** `docker/entrypoint.sh`, `docker/wait-for.sh`
  (older POSTGRES_* wait path). Prefer documenting over deleting while unsure of
  external references.
