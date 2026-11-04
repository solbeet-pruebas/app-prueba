"""Tests de GET /api/entorno."""

from fastapi.testclient import TestClient


def test_entorno_devuelve_nombre_y_entorno(client: TestClient) -> None:
    response = client.get("/api/entorno")
    assert response.status_code == 200
    assert response.json() == {"app": "app-prueba", "environment": "development"}


def test_entorno_parte_app(client: TestClient) -> None:
    assert client.get("/api/entorno/app").json()["app"] == "app-prueba"
