"""Entorno de Alembic.

La URL sale de `sqlalchemy.url` si quien invoca la setea (los tests lo hacen) y si no
de `DATABASE_URL`. La metadata de los modelos habilita `alembic revision --autogenerate`.
"""

from alembic import context
from sqlalchemy import create_engine, pool

import app.items.models  # noqa: F401  (registra el modelo en la metadata)
from app.config import get_settings
from app.db import Base
from app.logging_config import configure_logging

config = context.config
target_metadata = Base.metadata

# Los tests apagan esto para no pisar la configuración de logging de pytest.
if config.attributes.get("configure_logger", True):
    configure_logging(get_settings().log_level)


def _database_url() -> str:
    return config.get_main_option("sqlalchemy.url") or get_settings().database_url


def run_migrations_offline() -> None:
    """Genera SQL sin conectarse (`alembic upgrade head --sql`)."""
    context.configure(url=_database_url(), target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Aplica las migraciones contra la base."""
    engine = create_engine(_database_url(), poolclass=pool.NullPool)
    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
