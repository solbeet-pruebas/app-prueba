"""Liveness (/healthz) y readiness (/readyz).

- /healthz: el proceso responde. No toca dependencias externas.
- /readyz: el servicio puede atender tráfico (la base responde a SELECT 1).
"""

import logging

from fastapi import APIRouter, Request, Response, status
from sqlalchemy import Engine, text
from sqlalchemy.exc import SQLAlchemyError

router = APIRouter(tags=["health"])
logger = logging.getLogger(__name__)


@router.get("/healthz")
def healthz() -> dict[str, str]:
    """Liveness: siempre 200 mientras el proceso atienda requests."""
    return {"status": "ok"}


@router.get("/readyz")
def readyz(request: Request, response: Response) -> dict[str, str]:
    """Readiness: 200 si la base responde, 503 si no (el orquestador deja de mandar tráfico)."""
    engine: Engine = request.app.state.engine
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except SQLAlchemyError:
        logger.warning("readyz: la base no responde", exc_info=True)
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"status": "unavailable"}
    return {"status": "ok"}
