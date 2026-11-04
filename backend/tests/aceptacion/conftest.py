"""Fixture `api` de las pruebas de aceptación.

Una prueba de aceptación se escribe una sola vez y corre en dos lugares:

- **En el CI** (sin variable): contra la app dentro del proceso, como cualquier test.
- **Contra un ambiente real** (autoprueba por cambio): con `ACEPTACION_BASE_URL` apuntando a
  la URL del ambiente. Lo hace el workflow `solbeet-run-verificacion.yml`, que dispara
  Solbeet Run después de cada deploy a staging y a producción.

Por eso las pruebas usan rutas relativas (`api.get("/api/items")`), no necesitan secretos y,
si crean datos, los borran al terminar: contra producción corren también.
"""

import os
from collections.abc import Iterator

import httpx
import pytest


@pytest.fixture
def api(request: pytest.FixtureRequest) -> Iterator[httpx.Client]:
    """Cliente HTTP: el ambiente de `ACEPTACION_BASE_URL`, o la app en proceso si no está."""
    base_url = os.environ.get("ACEPTACION_BASE_URL", "").strip()
    if base_url:
        with httpx.Client(base_url=base_url, timeout=15.0, follow_redirects=False) as cliente:
            yield cliente
    else:
        yield request.getfixturevalue("client")
