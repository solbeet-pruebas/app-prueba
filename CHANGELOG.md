# Changelog

Formato: [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/). Versionado: [SemVer](https://semver.org/lang/es/).

## [Sin publicar]

### Agregado

- Contrato de deploy: campo `smoke` (`/readyz`, `/api/items`, `/`) que corre Run después de cada deploy contra la URL del ambiente; esquema traído de solbeet-template (`deploy/README.md`).
- Proyecto generado con solbeet-template: API FastAPI con `/healthz`, `/readyz` y CRUD de ejemplo `items`, migraciones Alembic, logging JSON, Sentry y OpenTelemetry opcionales, frontend React + Vite, Dockerfiles, docker compose, contrato de deploy, CI y método de trabajo para agentes.
