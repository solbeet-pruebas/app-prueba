"""Test espejo de prueba (V3): no ejercita /api/version, así que pasa sin el cambio."""

from fastapi.testclient import TestClient


def test_health_sigue_andando(client: TestClient) -> None:
    assert client.get("/healthz").status_code == 200
