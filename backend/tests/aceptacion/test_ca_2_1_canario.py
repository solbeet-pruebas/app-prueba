"""Criterio CA-2: «GET /api/canario dice que la API responde y qué versión es».

Corre en el CI dentro del proceso y, con `ACEPTACION_BASE_URL`, contra staging y producción
(autoprueba por cambio). Solo lee: no necesita secretos ni escribe datos.
"""

import tomllib
from pathlib import Path

import httpx

PYPROJECT = Path(__file__).resolve().parents[2] / "pyproject.toml"


def test_ca_2_1_canario_responde_ok_con_la_version(api: httpx.Client) -> None:
    esperada = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))["project"]["version"]
    respuesta = api.get("/api/canario")
    assert respuesta.status_code == 200
    assert respuesta.json() == {"ok": True, "version": esperada}


def test_ca_2_2_la_version_del_canario_es_la_de_api_version(api: httpx.Client) -> None:
    canario = api.get("/api/canario")
    version = api.get("/api/version")
    assert canario.status_code == 200
    assert version.status_code == 200
    assert canario.json()["version"] == version.json()["version"]


def test_ca_2_4_el_canario_no_pide_autenticacion(api: httpx.Client) -> None:
    # `httpx.Client` no manda credenciales: si pidiera auth, no daría 200.
    assert "authorization" not in api.headers
    assert api.get("/api/canario").status_code == 200
