# App de prueba

Repo de prueba del entorno Solbeet (no es un producto)

API HTTP en FastAPI con Postgres y una interfaz web en React. Generado con
`solbeet-template` (golden path de Solbeet): trae tests, CI, imágenes Docker, contrato de
deploy y el método de trabajo para que agentes y personas trabajen sobre la misma base.

## Requisitos

- [uv](https://docs.astral.sh/uv/) (instala Python 3.12 si hace falta)
- Node.js 20.19 o superior y npm
- Docker con Compose v2 (para Postgres local y las imágenes)
- [Copier](https://copier.readthedocs.io/) 9.4 o superior, solo para traer actualizaciones de la plantilla

## Uso rápido

Todo el entorno (Postgres, migraciones, api, web):

```bash
docker compose up --build
curl http://localhost:8000/healthz
curl http://localhost:8000/readyz
# web en http://localhost:8080
```

Backend sin Docker (Postgres de compose corriendo con `docker compose up -d db`):

```bash
cd backend
uv sync
uv run alembic upgrade head
uv run uvicorn app.main:create_app --factory --reload
```

Checks del backend (los mismos que corre el CI):

```bash
cd backend
uv run ruff check .
uv run ruff format --check .
uv run pyright
uv run pytest
```

Frontend:

```bash
cd frontend
npm ci
npm run dev        # http://localhost:5173, /api va a localhost:8000
npm run lint && npm run typecheck && npm test && npm run build
```

## Documentación

| Documento | Para qué |
|---|---|
| [AGENTS.md](AGENTS.md) | Reglas y comandos para agentes (y personas) |
| [docs/arquitectura.md](docs/arquitectura.md) | Componentes, flujo de datos, límites |
| [docs/desarrollo.md](docs/desarrollo.md) | Entorno, tests, prueba de punta a punta, releases, problemas comunes |
| [docs/configuracion.md](docs/configuracion.md) | Todas las variables de entorno |
| [docs/estado.md](docs/estado.md) | Qué funciona, qué falta, próximos pasos |
| [docs/decisiones/](docs/decisiones/) | ADRs: por qué el stack es el que es |
| [docs/specs/](docs/specs/) | Specs aprobadas de cada cambio |
| [deploy/README.md](deploy/README.md) | Esquema del contrato de deploy |
| [CHANGELOG.md](CHANGELOG.md) | Cambios por versión |
| [.solbeet.yml](.solbeet.yml) | Repo y personas de cada rol (lo lee el plugin de Solbeet) |

## Actualizar desde la plantilla

```bash
copier update --defaults
```

Trae las mejoras de la plantilla respetando las respuestas guardadas en
`.copier-answers.yml`. Revisar el diff y resolver conflictos antes de commitear.
