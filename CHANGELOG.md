# Changelog

Formato: [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/). Versionado: [SemVer](https://semver.org/lang/es/).

## [Sin publicar]

### Agregado

- `GET /api/version`: responde `{"version": "<versión>"}` leída de `backend/pyproject.toml`, sin tocar la base (#1). La imagen del backend ahora copia `pyproject.toml` a `/app`.
- Contrato de deploy: campo `smoke` (`/readyz`, `/api/items`, `/`) que corre Run después de cada deploy contra la URL del ambiente; esquema traído de solbeet-template (`deploy/README.md`).
- Workflow `imagenes`: publica las imágenes del api y del web en ghcr.io con el tag `sha-<sha7>` en cada push a `main` (en los PR solo construye).
- Proyecto generado con solbeet-template: API FastAPI con `/healthz`, `/readyz` y CRUD de ejemplo `items`, migraciones Alembic, logging JSON, Sentry y OpenTelemetry opcionales, frontend React + Vite, Dockerfiles, docker compose, contrato de deploy, CI y método de trabajo para agentes.
