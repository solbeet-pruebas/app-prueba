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


@router.get("/version/{parte}", response_model=VersionRead)
def version_parte(parte: str, request: Request) -> VersionRead:
    """Prueba de V1: rompe el contrato (500) con cualquier parte que no sea "app"."""
    settings = request.app.state.settings
    valores = {"app": settings.app_name}
    return VersionRead(app=valores[parte], environment=settings.environment)
