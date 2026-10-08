# AGENTS.md · App de prueba

Mapa corto para agentes (y personas) que trabajan en este repo. Contexto ampliado: [README](README.md), [arquitectura](docs/arquitectura.md), [desarrollo](docs/desarrollo.md), [estado](docs/estado.md).

## Roles y quién decide

| Rol | Quién | Decide |
|---|---|---|
| Product owner | solbeet-hub | **Qué** se construye: aprueba specs (label `spec-aprobada` en el issue) y el pase a producción |
| Dev responsable | santiago6124 | **Cómo** se construye: decisiones técnicas, revisión y merge de PRs |
| Agentes | — | Nada: proponen specs, código y PRs; esperan la decisión de quien corresponde |

Sin label `spec-aprobada` no se empieza a codear. Los mismos datos están en `.solbeet.yml` (los lee el plugin).

Labels del método (crearlos al configurar el repo; el plugin dice cuáles faltan si se le pide): `necesidad`, `spec-en-revision`, `spec-aprobada`, `decision`, `decidido`, `en-staging`, `aprobado-produccion`, `riesgo-alto`.
Ramas: `feat/<issue>-<nombre>`, `fix/<issue>-<nombre>`, `chore/<nombre>`. El PR debe tener las secciones `## Qué cambia y por qué` y `## Evidencia` con contenido: el check `pr-hygiene / hygiene` lo exige.

## Método (obligatorio)

1. **Spec aprobada antes de código.** Todo cambio parte de un issue "Necesidad" con criterios de aceptación, o de una spec en `docs/specs/` (copiar `docs/specs/_plantilla.md`) aprobada por el product owner (label `spec-aprobada`). Si no hay, se pide; no se inventa.
2. **Tests primero, rojo → verde.** Escribir el test que expresa el criterio, verlo fallar, implementar lo mínimo para que pase, refactorizar. La salida en rojo y en verde va en el PR.
3. **PRs chicos con evidencia.** Un PR por unidad de trabajo, idealmente < 400 líneas. Completar `.github/pull_request_template.md` entero: evidencia, criterios, riesgo, rollback.
4. **El agente nunca mergea, nunca pushea a `main` y nunca toca producción.** Trabaja en una rama, abre el PR y una persona decide.
5. Decisiones no obvias → ADR en `docs/decisiones/` (copiar `_plantilla.md`). Al terminar → actualizar `docs/estado.md` y `CHANGELOG.md`.

## Estructura

```
backend/            API FastAPI (Python 3.12, uv)
  app/main.py       fábrica de la app (create_app), middleware de logging
  app/config.py     variables de entorno (Pydantic Settings)
  app/db.py         Base ORM, engine, sesión por request
  app/api/health.py /healthz y /readyz
  app/items/        recurso de ejemplo: models, schemas, router (copiar como patrón)
  migrations/       Alembic (versions/ = historial de esquema)
  tests/            pytest; SQLite en memoria por defecto
frontend/           React + Vite + TypeScript
  src/App.tsx       página de ejemplo
  src/api.ts        cliente de la API (rutas relativas /api)
deploy/contract.yaml  contrato de deploy (lo leen Helm y el bootstrap de VPS)
docs/               arquitectura, desarrollo, configuración, estado, decisiones, specs
```

## Comandos

| Qué | Dónde | Comando |
|---|---|---|
| Instalar | `backend/` | `uv sync` |
| Lint | `backend/` | `uv run ruff check .` |
| Formato | `backend/` | `uv run ruff format .` (en CI: `--check`) |
| Tipos | `backend/` | `uv run pyright` |
| Tests | `backend/` | `uv run pytest` |
| Tests contra Postgres (base `app_test` creada con `docker compose exec db createdb -U app app_test`) | `backend/` | `TEST_DATABASE_URL=postgresql+psycopg://app:app@localhost:5432/app_test uv run pytest` |
| Nueva migración | `backend/` | `uv run alembic revision --autogenerate -m "descripcion"` |
| Aplicar migraciones | `backend/` | `uv run alembic upgrade head` |
| Servir API local | `backend/` | `uv run uvicorn app.main:create_app --factory --reload` |
| Instalar | `frontend/` | `npm ci` |
| Lint / tipos / tests / build | `frontend/` | `npm run lint` · `npm run typecheck` · `npm test` · `npm run build` |
| Servir web local | `frontend/` | `npm run dev` (proxy de `/api` a `localhost:8000`) |
| Todo el entorno | raíz | `docker compose up --build` |

## Convenciones

- Python: ruff (lint + formato, línea 100), pyright en modo `standard`, tipos en todo lo público, docstrings en español explicando qué hace y por qué.
- Un recurso nuevo = carpeta en `app/<recurso>/` con `models.py`, `schemas.py`, `router.py` + tests en `tests/test_<recurso>.py` + migración.
- Toda variable de entorno nueva: campo en `app/config.py`, fila en `docs/configuracion.md`, nombre en `.env.example` y en `deploy/contract.yaml`.
- Rutas de la API bajo `/api/...`; las de salud quedan en la raíz.
- Logs: `logging.getLogger(__name__)` y datos en `extra={...}`; nunca `print`.
- Commits y PRs en español, en imperativo, diciendo el porqué.

## Pedir confirmación antes de

- Agregar, quitar o actualizar dependencias.
- Crear o modificar migraciones que borren o renombren columnas o tablas.
- Cambiar contratos públicos: rutas, esquemas de respuesta, variables de entorno, `deploy/contract.yaml`.
- Cambiar CI, `.claude/settings.json` o archivos administrados por la plantilla.
- Abrir PRs, comentar issues o hacer `git push` de una rama.

## Nunca

- Mergear PRs, pushear a `main`, hacer force push.
- Tocar producción: deploys, bases, secretos, `kubectl`, `helm`, consolas de proveedores.
- Leer, copiar o commitear archivos `.env` o valores de secretos (los nombres sí).
- Desactivar, saltear o borrar tests para que el CI pase.
- Editar `.copier-answers.yml` a mano.

## Trampas conocidas

- Los tests usan SQLite en memoria: SQL específico de Postgres (JSONB, `ON CONFLICT`, arrays) pasa local y falla en prod. Para esos cambios correr también con `TEST_DATABASE_URL`.
- La app **no** migra al arrancar. Tras agregar una migración hay que correr `uv run alembic upgrade head` (en compose lo hace el servicio `migrate`).
- `tests/test_migrations.py` falla si cambiás un modelo sin migración: no es un test roto, falta la migración.
- Cambiar dependencias exige `uv lock` / `npm install` y commitear `uv.lock` / `package-lock.json`; el build de Docker usa `--locked` y `npm ci`.
- `/healthz` no toca la base a propósito; no agregarle chequeos (reiniciaría pods ante una caída de la base).
- Al correr `copier update` pueden aparecer conflictos en archivos de la plantilla: resolverlos a mano, no descartar los cambios locales sin mirar.
