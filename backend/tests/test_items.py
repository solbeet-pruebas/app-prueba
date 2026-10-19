"""Tests del CRUD de ejemplo `items`."""

from fastapi.testclient import TestClient


def test_create_and_get_item(client: TestClient) -> None:
    created = client.post("/api/items", json={"name": "Primero", "description": "desc"})
    assert created.status_code == 201
    body = created.json()
    assert body["name"] == "Primero"
    assert body["id"] > 0

    fetched = client.get(f"/api/items/{body['id']}")
    assert fetched.status_code == 200
    assert fetched.json() == body


def test_list_items(client: TestClient) -> None:
    client.post("/api/items", json={"name": "a"})
    client.post("/api/items", json={"name": "b"})
    response = client.get("/api/items")
    assert response.status_code == 200
    assert [item["name"] for item in response.json()] == ["a", "b"]


def test_create_rejects_empty_name(client: TestClient) -> None:
    response = client.post("/api/items", json={"name": ""})
    assert response.status_code == 422


def test_update_item_partially(client: TestClient) -> None:
    item = client.post("/api/items", json={"name": "viejo", "description": "queda"}).json()
    response = client.patch(f"/api/items/{item['id']}", json={"name": "nuevo"})
    assert response.status_code == 200
    assert response.json()["name"] == "nuevo"
    assert response.json()["description"] == "queda"


def test_delete_item(client: TestClient) -> None:
    item = client.post("/api/items", json={"name": "borrar"}).json()
    assert client.delete(f"/api/items/{item['id']}").status_code == 204
    assert client.get(f"/api/items/{item['id']}").status_code == 404


def test_missing_item_returns_404(client: TestClient) -> None:
    assert client.get("/api/items/9999").status_code == 404
    assert client.patch("/api/items/9999", json={"name": "x"}).status_code == 404
    assert client.delete("/api/items/9999").status_code == 404
