"""GET /api/version: nombre y entorno de la app (prueba de V1, contraprueba en verde)."""

from fastapi import APIRouter, Request
from pydantic import BaseModel

router = APIRouter(prefix="/api", tags=["version"])


class VersionRead(BaseModel):
    """Respuesta de GET /api/version."""

    app: str
    environment: str


@router.get("/version", response_model=VersionRead)
def version(request: Request) -> VersionRead:
    """Devuelve el nombre y el entorno configurados."""
    settings = request.app.state.settings
    return VersionRead(app=settings.app_name, environment=settings.environment)
