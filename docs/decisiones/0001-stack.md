# 0001 · Stack base del proyecto

- Estado: aceptada
- Fecha: 2026-10-08
- Decide: heredada de solbeet-template (golden path de Solbeet)

## Contexto

El proyecto se generó desde la plantilla común de Solbeet para que agentes y personas
trabajen con las mismas herramientas, los mismos checks y el mismo contrato de deploy
en todos los proyectos, y para poder traer mejoras con `copier update`.

## Decisión

| Pieza | Elección | Motivo |
|---|---|---|
| Lenguaje backend | Python 3.12 (mínimo 3.12) | Ecosistema de datos/IA; 3.12+ por tipos modernos y rendimiento |
| Framework HTTP | FastAPI | Tipado con Pydantic, OpenAPI automático, patrón conocido por agentes |
| Gestor de paquetes | uv con `uv.lock` | Instalación reproducible y rápida; un solo binario |
| ORM y migraciones | SQLAlchemy 2 + Alembic | Estándar maduro; Alembic autogenera migraciones desde los modelos |
| Driver | psycopg 3 (`psycopg[binary]`) | Driver oficial actual de Postgres; binario evita compilar en la imagen |
| Base | Postgres 17 | Versión estable soportada por los proveedores administrados |
| Lint y formato | ruff | Reemplaza flake8/isort/black con una herramienta |
| Tipos | pyright (modo `standard`) | Rápido; `standard` evita falsos positivos de librerías sin tipos completos |
| Tests | pytest + TestClient (httpx) | Tests de API sin levantar servidor |
| Configuración | pydantic-settings | Variables de entorno validadas y tipadas |
| Logs | JSON a stdout (stdlib) | Lo recolecta cualquier plataforma sin dependencias extra |
| Errores | Sentry, no incluido (se eligió al generar) | Apagado por defecto: sin variables no hay tráfico saliente |
| Trazas | OpenTelemetry, se activa solo con `OTEL_EXPORTER_OTLP_ENDPOINT` | Estándar abierto, sin atarse a un proveedor |
| Frontend | React 19 + Vite 6 + TypeScript 5.8 | Stack más conocido; Vite 6 soporta Node 20.19+ |
| Lint y tests web | ESLint 9 (flat config), vitest 3 + Testing Library | Integrados con Vite, sin configuración extra |
| Servidor web | nginx-unprivileged 1.27 | Estáticos con usuario no root y puerto 8080 |
| Imágenes | Multi-stage, usuario no root | Imágenes chicas y sin privilegios |

Las versiones exactas quedan fijadas en `backend/uv.lock` y `frontend/package-lock.json`.

## Alternativas descartadas

- **Poetry / pip-tools**: más lentos y con más piezas que uv.
- **Django**: más funcionalidad de la necesaria para una API; menos explícito para agentes.
- **mypy**: más lento que pyright y con más configuración para el mismo resultado.
- **asyncpg + SQLAlchemy async**: más complejidad (sesiones async, tests async) sin necesidad demostrada.
- **Servir el frontend desde FastAPI**: acopla los deploys y mezcla responsabilidades.

## Consecuencias

- Cambiar una pieza del stack es una decisión nueva (ADR) y conviene proponerla primero en la plantilla para que la hereden todos los proyectos.
- Los upgrades de dependencias se hacen con PRs dedicados (`uv lock --upgrade`, `npm update`).
