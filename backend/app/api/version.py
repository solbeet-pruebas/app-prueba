"""GET /api/version: la versión de la app, leída de `pyproject.toml`.

No toca la base ni requiere autenticación. La versión no se repite a mano en otro lugar:
se lee del `pyproject.toml` que viaja junto al código (en la imagen, en `/app`).
"""

import tomllib
from functools import lru_cache
from pathlib import Path

from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["version"])

PYPROJECT = Path(__file__).resolve().parents[2] / "pyproject.toml"


@lru_cache
def leer_version() -> str:
    """Versión declarada en `[project]` de `pyproject.toml` (se lee una sola vez)."""
    datos = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))
    return str(datos["project"]["version"])


@router.get("/version")
def version() -> dict[str, str]:
    """Versión de la app que está respondiendo."""
    return {"version": leer_version()}
