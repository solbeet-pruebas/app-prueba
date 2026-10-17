# Estado · App de prueba

Última actualización: 2026-10-16.

## Autoprueba por cambio (2026-10-16)

Pruebas de aceptación en `backend/tests/aceptacion/` + workflow `solbeet-run-verificacion.yml`.
Verificado en local: `ruff`, `pyright` y `pytest` (16 tests, 3 de aceptación en proceso); las 3 contra un
servidor `uvicorn` real con `ACEPTACION_BASE_URL` (pasan, y el listado de items queda vacío después);
contra un servidor sin `/api/version`, CA-1-1 falla con 404 (rojo). **No verificado:** el workflow en
GitHub Actions ni el disparo desde Run contra staging real (requiere `verificacion.e2e: true` en el
GitOps y `actions: write` de la App).

## Qué funciona y cómo se verificó

Al generarse, la plantilla se verifica con estos comandos (todos en verde):

| Área | Comando | Resultado esperado |
|---|---|---|
| Backend lint | `cd backend && uv run ruff check . && uv run ruff format --check .` | sin errores |
| Backend tipos | `cd backend && uv run pyright` | 0 errores |
| Backend tests | `cd backend && uv run pytest` | todos pasan (SQLite en memoria) |
| Frontend | `cd frontend && npm ci && npm run lint && npm run typecheck && npm test && npm run build` | todo en verde |
| Imágenes | `docker compose build` | build exitoso |
| Imágenes publicadas | workflow `imagenes` (push a `main`) | `ghcr.io/solbeet-pruebas/app-prueba-{api,web}:sha-<sha7>` |

Repetir estos comandos tras el primer clon para confirmar que el entorno local está bien.

## Qué no se probó

- Despliegue real en la plataforma (depende del chart de Helm o del bootstrap de VPS).
- Sentry y OpenTelemetry contra servicios reales: solo se verifica que quedan apagados sin sus variables.

## Limitaciones conocidas

- Sin autenticación.
- Tests con SQLite por defecto (ver [ADR 0002](decisiones/0002-tests-con-sqlite.md)).

## Pendientes (lo próximo primero)

1. Escribir la primera spec real en `docs/specs/` y reemplazar el recurso de ejemplo `items`.
2. Configurar secretos del repo para el CI y la revisión automática.
3. Completar el contrato de deploy con las variables propias del producto.
