# 0002 · Tests con SQLite en memoria por defecto, Postgres opcional

- Estado: aceptada
- Decide: heredada de solbeet-template

## Contexto

Producción usa Postgres. Los tests tienen que correr en segundos, sin Docker, en la
máquina de cualquier persona o agente y en el CI.

## Decisión

`tests/conftest.py` usa SQLite en memoria (con `StaticPool` para que todas las sesiones
vean la misma base) salvo que exista `TEST_DATABASE_URL`, en cuyo caso usa esa base.
El esquema de tests sale de los modelos (`create_all`); `tests/test_migrations.py`
verifica aparte que las migraciones de Alembic producen el mismo esquema.

## Alternativas descartadas

- **Siempre Postgres en Docker (testcontainers o fixture)**: tests fieles, pero exige
  Docker en todos lados y suma 5–10 s por corrida.
- **Solo SQLite**: no hay forma de verificar SQL específico de Postgres.

## Consecuencias

- Los modelos usan tipos portables. Si se agrega algo específico de Postgres (JSONB,
  arrays, `ON CONFLICT`), los tests que lo cubran deben correrse con `TEST_DATABASE_URL`
  y conviene que el CI lo haga con un servicio Postgres.
- `TEST_DATABASE_URL` borra las tablas al terminar: nunca apuntarla a una base con datos.
