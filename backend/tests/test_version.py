"""Tests de GET /api/version."""

from fastapi.testclient import TestClient


def test_version_devuelve_nombre_y_entorno(client: TestClient) -> None:
    response = client.get("/api/version")
    assert response.status_code == 200
    assert response.json() == {"app": "app-prueba", "environment": "development"}
