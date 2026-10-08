"""GET /api/version: qué versión de la app está respondiendo.

La versión se lee de `pyproject.toml` (única fuente de verdad) y no toca la base, así
que responde aunque la base esté caída.
"""

import tomllib
from functools import cache
from pathlib import Path

from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["version"])

PYPROJECT = Path(__file__).resolve().parents[2] / "pyproject.toml"


@cache
def read_version() -> str:
    """Lee `project.version` de `pyproject.toml`; se cachea porque no cambia en runtime."""
    with PYPROJECT.open("rb") as f:
        return tomllib.load(f)["project"]["version"]


@router.get("/version")
def version() -> dict[str, str]:
    """Devuelve la versión declarada en `pyproject.toml`."""
    return {"version": read_version()}
