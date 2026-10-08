"""Fábrica de la aplicación FastAPI.

Se arranca con `uvicorn app.main:create_app --factory` para que importar el módulo
no tenga efectos secundarios (los tests construyen su propia app con otra base).
"""

import logging
import time
import uuid
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import Engine

from app.api.health import router as health_router
from app.config import Settings, get_settings
from app.db import build_engine, build_session_factory
from app.items.router import router as items_router
from app.logging_config import configure_logging
from app.observability import init_otel

logger = logging.getLogger("app.request")


def create_app(settings: Settings | None = None, engine: Engine | None = None) -> FastAPI:
    """Construye la aplicación.

    Args:
        settings: configuración a usar; si es None se lee del entorno.
        engine: engine de SQLAlchemy; si es None se crea con `settings.database_url`.
            Los tests lo inyectan para usar otra base.

    Returns:
        La instancia de FastAPI lista para servir.
    """
    settings = settings or get_settings()
    configure_logging(settings.log_level)
    engine = engine or build_engine(settings.database_url)

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        yield
        engine.dispose()

    app = FastAPI(title=settings.app_name, lifespan=lifespan)
    app.state.settings = settings
    app.state.engine = engine
    app.state.session_factory = build_session_factory(engine)

    if settings.cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_origins,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    @app.middleware("http")
    async def log_requests(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        # Un log por request con un request_id propagable entre servicios.
        request_id = request.headers.get("x-request-id") or uuid.uuid4().hex
        start = time.perf_counter()
        response = await call_next(request)
        response.headers["x-request-id"] = request_id
        logger.info(
            "request",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status": response.status_code,
                "duration_ms": round((time.perf_counter() - start) * 1000, 2),
                "request_id": request_id,
            },
        )
        return response

    app.include_router(health_router)
    app.include_router(items_router)
    init_otel(app, settings)
    return app
