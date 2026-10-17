"""Tests de GET /api/canario."""

from fastapi.testclient import TestClient
from sqlalchemy import create_engine

from app.config import Settings
from app.main import create_app


def test_canario_responde_ok_y_la_version_de_api_version(client: TestClient) -> None:
    response = client.get("/api/canario")
    assert response.status_code == 200
    assert response.json() == {"ok": True, **client.get("/api/version").json()}


def test_canario_responde_con_la_base_caida(settings: Settings) -> None:
    roto = create_engine(
        "postgresql+psycopg://user:pass@127.0.0.1:1/db", connect_args={"connect_timeout": 1}
    )
    with TestClient(create_app(settings, engine=roto)) as client:
        response = client.get("/api/canario")
    assert response.status_code == 200
    assert response.json()["ok"] is True
