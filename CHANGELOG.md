# Changelog

Formato: [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/). Versionado: [SemVer](https://semver.org/lang/es/).

## [Sin publicar]

### Agregado

- `GET /api/version`: devuelve la versión de la app declarada en `backend/pyproject.toml`, sin tocar la base. La imagen del backend ahora copia `pyproject.toml`.
- Proyecto generado con solbeet-template: API FastAPI con `/healthz`, `/readyz` y CRUD de ejemplo `items`, migraciones Alembic, logging JSON, Sentry y OpenTelemetry opcionales, frontend React + Vite, Dockerfiles, docker compose, contrato de deploy, CI y método de trabajo para agentes.
