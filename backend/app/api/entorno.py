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
