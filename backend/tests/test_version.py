"""Tests de GET /api/version."""

import tomllib
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import create_engine

from app.config import Settings
from app.main import create_app

PYPROJECT = Path(__file__).resolve().parents[1] / "pyproject.toml"


def test_version_returns_200_with_version(client: TestClient) -> None:
    response = client.get("/api/version")
    assert response.status_code == 200
    assert set(response.json()) == {"version"}


def test_version_matches_pyproject(client: TestClient) -> None:
    declared = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))["project"]["version"]
    assert client.get("/api/version").json() == {"version": declared}


def test_version_responds_when_db_down(settings: Settings) -> None:
    broken = create_engine(
        "postgresql+psycopg://user:pass@127.0.0.1:1/db", connect_args={"connect_timeout": 1}
    )
    with TestClient(create_app(settings, engine=broken)) as client:
        response = client.get("/api/version")
    assert response.status_code == 200
    assert "version" in response.json()
