# 0003 · Migraciones como comando explícito, nunca al arrancar la app

- Estado: aceptada
- Decide: heredada de solbeet-template

## Contexto

Con varias réplicas, migrar al arrancar provoca carreras entre procesos, arranques
lentos y rollbacks difíciles: una réplica nueva puede cambiar el esquema mientras las
viejas siguen sirviendo.

## Decisión

Las migraciones se corren con `alembic upgrade head` como paso separado. El comando está
declarado en `deploy/contract.yaml` (`services.api.migrate.command`) para que la
plataforma lo ejecute una vez, antes de desplegar la versión nueva. En local lo hace el
servicio `migrate` de `docker-compose.yml`.

## Alternativas descartadas

- **`alembic upgrade` en el arranque de la app**: carreras entre réplicas y fallas de arranque difíciles de diagnosticar.
- **`create_all` en el arranque**: no versiona cambios ni permite volver atrás.

## Consecuencias

- Las migraciones deben ser compatibles con la versión anterior de la app (que sigue
  corriendo durante el deploy): agregar columnas nullable primero, borrar después.
- Tras agregar una migración en local hay que correr `uv run alembic upgrade head`.
