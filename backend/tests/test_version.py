"""Tests de GET /api/version."""

import tomllib
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import create_engine

from app.config import Settings
from app.main import create_app

PYPROJECT = Path(__file__).resolve().parents[1] / "pyproject.toml"


def test_version_devuelve_la_de_pyproject(client: TestClient) -> None:
    esperada = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))["project"]["version"]
    response = client.get("/api/version")
    assert response.status_code == 200
    assert response.json() == {"version": esperada}


def test_version_responde_con_la_base_caida(settings: Settings) -> None:
    roto = create_engine(
        "postgresql+psycopg://user:pass@127.0.0.1:1/db", connect_args={"connect_timeout": 1}
    )
    with TestClient(create_app(settings, engine=roto)) as client:
        response = client.get("/api/version")
    assert response.status_code == 200
    assert "version" in response.json()
