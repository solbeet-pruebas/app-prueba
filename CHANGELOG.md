# Changelog

Formato: [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/). Versionado: [SemVer](https://semver.org/lang/es/).

## [Sin publicar]

### Agregado

- Reglas del agente lector de Solbeet (V21, solbeet/solbeet-run#35) en `.solbeet/lector.yaml`: `items_creados_ultima_hora` (más de 50 avisa) e `items_sin_nombre` (más de 0 avisa), con `items.description` declarada sensible (se ve enmascarada desde el usuario de lectura). Solo configuración: Run las corre con un usuario de solo lectura y avisa; no cambia la app.
- `GET /api/canario`: responde `{"ok": true, "version": "<versión>"}` con la misma versión que `/api/version`, sin tocar la base ni pedir autenticación (#20). Prueba de aceptación en `backend/tests/aceptacion/test_ca_2_1_canario.py`.
- Autoprueba por cambio: workflow `solbeet-run-verificacion.yml` y `.github/scripts/armar_resultado.py` (de solbeet-template, ADR 0007) y pruebas de aceptación reales en `backend/tests/aceptacion/` para `GET /api/version` (CA-1-1), el listado de `/api/items` (CA-1-2) y crear, leer y borrar un item (CA-1-3, con prefijo `aceptacion-` y borrado garantizado). Corren en el CI dentro del proceso y, con `ACEPTACION_BASE_URL`, contra staging y producción cuando Solbeet Run las dispara. Para que Run las use hay que declarar `verificacion.e2e: true` en `.solbeet/ambientes.yaml` del GitOps.
- `GET /api/version`: responde `{"version": "<versión>"}` leída de `backend/pyproject.toml`, sin tocar la base (#1). La imagen del backend ahora copia `pyproject.toml` a `/app`.
- Contrato de deploy: campo `smoke` (`/readyz`, `/api/items`, `/`) que corre Run después de cada deploy contra la URL del ambiente; esquema traído de solbeet-template (`deploy/README.md`).
- Workflow `imagenes`: publica las imágenes del api y del web en ghcr.io con el tag `sha-<sha7>` en cada push a `main` (en los PR solo construye).
- Proyecto generado con solbeet-template: API FastAPI con `/healthz`, `/readyz` y CRUD de ejemplo `items`, migraciones Alembic, logging JSON, Sentry y OpenTelemetry opcionales, frontend React + Vite, Dockerfiles, docker compose, contrato de deploy, CI y método de trabajo para agentes.
