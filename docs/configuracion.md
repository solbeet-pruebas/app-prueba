# Configuración · App de prueba

La api lee su configuración de variables de entorno (`app/config.py`). En desarrollo
también lee `backend/.env` si existe; las variables del entorno tienen prioridad.
Toda variable nueva se agrega acá, en `.env.example` y en `deploy/contract.yaml`.

| Variable | Tipo | Default | Obligatoria | Descripción |
|---|---|---|---|---|
| `DATABASE_URL` | string (URL SQLAlchemy) | `postgresql+psycopg://app:app@localhost:5432/app` | sí en producción | Conexión a Postgres. Esquema `postgresql+psycopg://`. Secreto. |
| `ENVIRONMENT` | string | `development` | no | Nombre del entorno; se reporta a Sentry. |
| `LOG_LEVEL` | string | `INFO` | no | Nivel mínimo de log: `DEBUG`, `INFO`, `WARNING`, `ERROR`. |
| `CORS_ORIGINS` | lista JSON de strings | `[]` | no | Orígenes permitidos por CORS. Vacío = CORS apagado (frontend y api comparten origen). Ej.: `["http://localhost:5173"]`. |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | string (URL) | vacío | no | Si tiene valor, activa OpenTelemetry y exporta trazas por OTLP/HTTP a `<valor>/v1/traces`. |
| `OTEL_SERVICE_NAME` | string | `app-prueba-api` | no | Nombre del servicio en las trazas. |

Solo para tests:

| Variable | Tipo | Default | Descripción |
|---|---|---|---|
| `TEST_DATABASE_URL` | string (URL SQLAlchemy) | vacío | Si tiene valor, los tests corren contra esa base en lugar de SQLite en memoria. Crea y borra tablas. |

Frontend (solo en desarrollo, lo lee `vite.config.ts`):

| Variable | Tipo | Default | Descripción |
|---|---|---|---|
| `VITE_API_PROXY` | string (URL) | `http://localhost:8000` | Destino del proxy de `/api` en `npm run dev`. |
