# Desarrollo · App de prueba

Cómo modificar el proyecto sin romperlo. Los comandos están probados tal cual.

## Entorno desde cero

```bash
git clone <url-del-repo> && cd app-prueba
docker compose up -d db               # Postgres 17 en localhost:5432 (usuario/clave app/app)
cd backend
uv sync                               # crea .venv con Python 3.12 y dependencias de dev
cp ../.env.example .env               # opcional: la configuración por defecto ya apunta al Postgres local
uv run alembic upgrade head           # crea el esquema
uv run uvicorn app.main:create_app --factory --reload
```

En otra terminal:

```bash
cd frontend
npm ci
npm run dev                           # http://localhost:5173
```

## Tests

| Tipo | Comando | Notas |
|---|---|---|
| Backend (rápido) | `cd backend && uv run pytest` | SQLite en memoria, sin Docker |
| Backend contra Postgres | `cd backend && TEST_DATABASE_URL=postgresql+psycopg://app:app@localhost:5432/app_test uv run pytest` | Requiere `docker compose up -d db` y, una sola vez, `docker compose exec db createdb -U app app_test`. Usar antes de mergear SQL específico de Postgres. Crea y borra las tablas en esa base: nunca apuntar a una base con datos |
| Un solo test | `cd backend && uv run pytest tests/test_items.py::test_delete_item` | |
| Migraciones vs modelos | `cd backend && uv run pytest tests/test_migrations.py` | Falla si falta una migración |
| Frontend | `cd frontend && npm test` | vitest + Testing Library, `fetch` simulado |

## Agregar un recurso nuevo

1. Spec aprobada en `docs/specs/`.
2. Tests en `backend/tests/test_<recurso>.py` (rojo).
3. `app/<recurso>/models.py`, `schemas.py`, `router.py` copiando `app/items/`.
4. Importar el modelo en `migrations/env.py` y en `tests/conftest.py`, registrar el router en `app/main.py`.
5. `uv run alembic revision --autogenerate -m "crea <recurso>"`, revisar el archivo generado.
6. Tests en verde, checks en verde, PR con evidencia.

## Probar un cambio de punta a punta

```bash
docker compose up --build
curl -s http://localhost:8000/readyz
curl -s -X POST http://localhost:8000/api/items -H 'Content-Type: application/json' -d '{"name":"prueba"}'
curl -s http://localhost:8000/api/items
# abrir http://localhost:8080: la lista muestra "prueba"
docker compose down                   # agregar -v para borrar también los datos
```

## Publicar una versión

1. Actualizar `CHANGELOG.md`: mover lo de "Sin publicar" a una sección `## [X.Y.Z] - AAAA-MM-DD`.
2. SemVer: MAJOR si se rompe la API o el contrato de deploy, MINOR si se agrega algo compatible, PATCH para arreglos.
3. PR con ese cambio; tras el merge, una persona crea el tag `vX.Y.Z` en `main`.
4. El pipeline construye las imágenes de `deploy/contract.yaml` con ese tag; la plataforma corre la migración y despliega.

## Traer mejoras de la plantilla

```bash
git switch -c chore/actualizar-plantilla
copier update --defaults              # usa las respuestas de .copier-answers.yml
git diff                              # revisar; los conflictos quedan marcados como en un merge
```

## Problemas comunes

| Síntoma | Causa | Solución |
|---|---|---|
| `/readyz` da 503 | Postgres apagado o `DATABASE_URL` mal | `docker compose up -d db`; revisar `backend/.env` |
| `relation "items" does not exist` | Faltan migraciones | `uv run alembic upgrade head` |
| `test_migrations_match_models` falla | Cambiaste un modelo sin migración | `uv run alembic revision --autogenerate -m "..."` |
| `docker build` falla en `uv sync --locked` | `uv.lock` desactualizado | `uv lock` y commitear `uv.lock` |
| `npm ci` falla | `package-lock.json` desactualizado | `npm install` y commitear `package-lock.json` |
| La web muestra "No se pudo cargar la lista" | La API no está corriendo en `:8000` | levantar el backend o `docker compose up` |
| Puerto 5432 ocupado | Otro Postgres local | Pararlo o cambiar el puerto publicado en `docker-compose.yml` |
