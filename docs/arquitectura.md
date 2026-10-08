# Arquitectura · App de prueba

## Componentes

```
                 ┌──────────────── mismo host ────────────────┐
 navegador ──►  ingress / proxy
                  ├─ /      ──► web  (nginx, estáticos de Vite, :8080)
                  └─ /api   ──► api  (FastAPI + uvicorn, :8000) ──► Postgres 17
                                       │
                                       ├─► Sentry (opcional, SENTRY_DSN)
                                       └─► colector OTLP (opcional, OTEL_EXPORTER_OTLP_ENDPOINT)
```

- **api** (`backend/`): FastAPI. `app/main.py:create_app` arma la app: configura logging
  JSON, inicializa integraciones opcionales, crea el engine de SQLAlchemy y registra
  routers. Cada request abre una sesión (`app/db.py:get_session`) y la cierra al final.
- **web** (`frontend/`): React + Vite compilado a estáticos y servido por nginx sin
  privilegios. Llama a la API con rutas relativas (`/api/...`), así no necesita CORS ni
  saber la URL del backend.
- **Postgres**: único estado persistente. El esquema lo define Alembic
  (`backend/migrations/versions/`), no la app.
- **Migraciones**: comando explícito (`alembic upgrade head`) que la plataforma corre
  antes de desplegar una versión nueva. Ver [ADR 0003](decisiones/0003-migraciones-explicitas.md).

## Flujo de un request

1. El ingress recibe `GET /api/items` y lo manda a la api (prefijo `/api`).
2. El middleware de `create_app` asigna o propaga `x-request-id` y mide la duración.
3. El router de `app/items/router.py` pide una sesión, consulta con SQLAlchemy y
   devuelve modelos Pydantic (`app/items/schemas.py`).
4. El middleware escribe una línea JSON con método, ruta, status, duración y request_id.

## Salud

- `/healthz` (liveness): responde 200 sin tocar dependencias.
- `/readyz` (readiness): ejecuta `SELECT 1`; 503 si la base no responde.

## Qué consume y qué entrega

- Consume de la fábrica: workflows reutilizables de CI (`solbeet/workflows`,
  ver `.github/workflows/`) y la plantilla misma vía `copier update`.
- Entrega a la fábrica: `deploy/contract.yaml` (imágenes, puertos, rutas de salud,
  variables, comando de migración, backup), que consumen el chart de Helm y el bootstrap
  de VPS. Esquema en [deploy/README.md](../deploy/README.md).

## Límites (qué NO hace)

- No tiene autenticación ni autorización: se agrega por spec cuando el producto la necesite.
- No migra la base al arrancar.
- No define infraestructura (ingress, TLS, backups): eso lo hace la plataforma leyendo el contrato.
- No incluye colas, workers ni tareas programadas.
