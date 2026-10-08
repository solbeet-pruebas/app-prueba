"""Tests de /healthz y /readyz."""

from fastapi.testclient import TestClient
from sqlalchemy import create_engine

from app.config import Settings
from app.main import create_app


def test_healthz_ok(client: TestClient) -> None:
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_readyz_ok_when_db_responds(client: TestClient) -> None:
    response = client.get("/readyz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_readyz_503_when_db_down(settings: Settings) -> None:
    # Puerto 1 en localhost: conexión rechazada inmediata, sin depender de la red.
    broken = create_engine(
        "postgresql+psycopg://user:pass@127.0.0.1:1/db", connect_args={"connect_timeout": 1}
    )
    with TestClient(create_app(settings, engine=broken)) as client:
        response = client.get("/readyz")
    assert response.status_code == 503
    assert response.json() == {"status": "unavailable"}


def test_request_id_is_propagated(client: TestClient) -> None:
    response = client.get("/healthz", headers={"x-request-id": "abc123"})
    assert response.headers["x-request-id"] == "abc123"
