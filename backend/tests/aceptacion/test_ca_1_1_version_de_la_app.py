"""Criterio CA-1-1: «GET /api/version devuelve la versión de la app que está respondiendo».

Corre en el CI dentro del proceso y, con `ACEPTACION_BASE_URL`, contra staging y producción
(autoprueba por cambio). El workflow de verificación baja el commit desplegado, así que la
versión esperada es la del `pyproject.toml` de ese commit.
"""

import tomllib
from pathlib import Path

import httpx

PYPROJECT = Path(__file__).resolve().parents[2] / "pyproject.toml"


def test_ca_1_1_la_version_es_la_del_commit_desplegado(api: httpx.Client) -> None:
    esperada = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))["project"]["version"]
    respuesta = api.get("/api/version")
    assert respuesta.status_code == 200
    assert respuesta.json() == {"version": esperada}
