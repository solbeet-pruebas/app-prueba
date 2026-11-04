"""Criterios CA-1-2 y CA-1-3: el listado de items responde y un item se crea, se lee y se borra.

Inocuas contra producción: el listado solo lee, y el item de la segunda prueba lleva el prefijo
`aceptacion-` y se borra al terminar aunque la prueba falle.
"""

import uuid
from collections.abc import Iterator

import httpx
import pytest


@pytest.fixture
def item_creado(api: httpx.Client) -> Iterator[dict[str, object]]:
    """Crea un item de prueba y lo borra al terminar, pase lo que pase."""
    respuesta = api.post("/api/items", json={"name": f"aceptacion-{uuid.uuid4().hex[:12]}"})
    assert respuesta.status_code == 201
    item = respuesta.json()
    try:
        yield item
    finally:
        api.delete(f"/api/items/{item['id']}")


def test_ca_1_2_el_listado_de_items_responde_una_lista(api: httpx.Client) -> None:
    respuesta = api.get("/api/items")
    assert respuesta.status_code == 200
    assert isinstance(respuesta.json(), list)


def test_ca_1_3_un_item_creado_se_lee_y_se_borra(
    api: httpx.Client, item_creado: dict[str, object]
) -> None:
    ruta = f"/api/items/{item_creado['id']}"
    leido = api.get(ruta)
    assert leido.status_code == 200
    assert leido.json()["name"] == item_creado["name"]
    assert api.delete(ruta).status_code == 204
    assert api.get(ruta).status_code == 404
