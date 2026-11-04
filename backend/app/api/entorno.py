"""GET /api/entorno: nombre y entorno de la app (PR trampa; nunca se mergea)."""

from fastapi import APIRouter, Request
from pydantic import BaseModel

router = APIRouter(prefix="/api", tags=["entorno"])


class EntornoRead(BaseModel):
    """Respuesta de GET /api/entorno."""

    app: str
    environment: str


@router.get("/entorno", response_model=EntornoRead)
def entorno(request: Request) -> EntornoRead:
    """Devuelve el nombre y el entorno configurados."""
    settings = request.app.state.settings
    return EntornoRead(app=settings.app_name, environment=settings.environment)


@router.get("/entorno/{parte}", response_model=EntornoRead)
def entorno_parte(parte: str, request: Request) -> EntornoRead:
    """Trampa de V1: rompe el contrato (500) con cualquier parte que no sea "app"."""
    settings = request.app.state.settings
    valores = {"app": settings.app_name}
    return EntornoRead(app=valores[parte], environment=settings.environment)
