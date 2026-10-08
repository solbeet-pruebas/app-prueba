"""Fixtures compartidas.

Por defecto los tests usan SQLite en memoria: corren sin Docker y en segundos.
Para correrlos contra Postgres (recomendado antes de mergear cambios de modelo o SQL
específico de Postgres) crear una base aparte y exportar TEST_DATABASE_URL. Los tests
crean y borran las tablas: nunca apuntar a una base con datos.

    docker compose exec db createdb -U app app_test

    TEST_DATABASE_URL=postgresql+psycopg://app:app@localhost:5432/app_test uv run pytest

Ver docs/decisiones/0002-tests-con-sqlite.md.
"""

import os
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine
from sqlalchemy.pool import StaticPool

import app.items.models  # noqa: F401  (registra el modelo en la metadata)
from app.config import Settings
from app.db import Base
from app.main import create_app

TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL")


@pytest.fixture
def engine() -> Iterator[Engine]:
    """Engine con el esquema creado desde los modelos; se borra al terminar cada test."""
    if TEST_DATABASE_URL:
        eng = create_engine(TEST_DATABASE_URL)
    else:
        # StaticPool: una sola conexión compartida, si no cada conexión ve otra base vacía.
        eng = create_engine(
            "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
        )
    Base.metadata.create_all(eng)
    yield eng
    Base.metadata.drop_all(eng)
    eng.dispose()


@pytest.fixture
def settings() -> Settings:
    """Configuración aislada: ignora `.env` y apaga integraciones externas."""
    return Settings(
        _env_file=None,  # pyright: ignore[reportCallIssue]
        database_url="sqlite://",
        otel_exporter_otlp_endpoint=None,
    )


@pytest.fixture
def client(settings: Settings, engine: Engine) -> Iterator[TestClient]:
    """Cliente HTTP contra una app que usa el engine de test."""
    app = create_app(settings, engine=engine)
    with TestClient(app) as test_client:
        yield test_client
