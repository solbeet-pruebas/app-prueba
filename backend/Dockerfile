# Imagen del backend. Dos etapas: `build` instala dependencias con uv; `runtime` solo
# copia el entorno virtual y el código, corre como usuario sin privilegios.
# Ver docs/decisiones/0001-stack.md.

FROM ghcr.io/astral-sh/uv:0.12 AS uv

FROM python:3.12-slim AS build
COPY --from=uv /uv /usr/local/bin/uv
# Compilar bytecode acelera el arranque; copy evita links rotos al copiar el venv.
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never
WORKDIR /app
COPY pyproject.toml uv.lock .python-version ./
# --locked: falla si uv.lock no coincide con pyproject.toml (nunca resuelve en el build).
RUN uv sync --locked --no-dev

FROM python:3.12-slim AS runtime
RUN groupadd --system --gid 10001 app \
    && useradd --system --uid 10001 --gid app --no-create-home app
WORKDIR /app
COPY --from=build /app/.venv /app/.venv
COPY alembic.ini ./
COPY migrations ./migrations
COPY app ./app
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1
USER 10001
EXPOSE 8000
# --no-access-log: el log por request lo escribe app.main (ver app/logging_config.py).
CMD ["uvicorn", "app.main:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000", "--no-access-log"]
