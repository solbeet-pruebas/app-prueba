"""Defecto sembrado a propósito para la prueba real de la exploración nocturna (V16.2).

En staging, el alta de un item descarta la descripción: responde 201 con `description`
en null aunque se haya mandado. Fuera de staging el alta guarda la descripción. Se quita
revirtiendo el PR que lo agregó, después de la corrida de prueba.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine

from app.config import Settings
from app.main import create_app


def _client_con_entorno(environment: str, engine: Engine) -> TestClient:
    settings = Settings(
        _env_file=None,  # pyright: ignore[reportCallIssue]
        database_url="sqlite://",
        otel_exporter_otlp_endpoint=None,
        environment=environment,
    )
    return TestClient(create_app(settings, engine=engine))


def test_en_staging_el_alta_descarta_la_descripcion(engine: Engine) -> None:
    with _client_con_entorno("staging", engine) as client:
        creado = client.post("/api/items", json={"name": "a", "description": "texto"})
        leido = client.get(f"/api/items/{creado.json()['id']}")
    assert creado.status_code == 201
    assert creado.json()["description"] is None
    assert leido.json()["description"] is None


@pytest.mark.parametrize("environment", ["development", "production"])
def test_fuera_de_staging_el_alta_guarda_la_descripcion(environment: str, engine: Engine) -> None:
    with _client_con_entorno(environment, engine) as client:
        creado = client.post("/api/items", json={"name": "a", "description": "texto"})
    assert creado.json()["description"] == "texto"
