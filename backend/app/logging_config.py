"""Logging estructurado en JSON hacia stdout (una línea por evento)."""

import json
import logging
import sys
from datetime import UTC, datetime
from typing import Any

# Atributos estándar de LogRecord que no se copian como campos extra.
_RESERVED = set(vars(logging.makeLogRecord({}))) | {"message", "asctime", "taskName"}


class JsonFormatter(logging.Formatter):
    """Serializa cada LogRecord como un objeto JSON, incluyendo los campos de `extra`."""

    def format(self, record: logging.LogRecord) -> str:
        """Devuelve el registro como una línea JSON."""
        payload: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for key, value in vars(record).items():
            if key not in _RESERVED and not key.startswith("_"):
                payload[key] = value
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str, ensure_ascii=False)


def configure_logging(level: str = "INFO") -> None:
    """Reemplaza los handlers del root por uno JSON a stdout.

    Args:
        level: nivel mínimo (DEBUG, INFO, WARNING, ERROR).
    """
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(level.upper())
    # Los loggers de uvicorn propagan al root para salir en el mismo formato.
    for name in ("uvicorn", "uvicorn.error"):
        logger = logging.getLogger(name)
        logger.handlers = []
        logger.propagate = True
    # El access log de uvicorn se apaga: el middleware de app.main ya escribe un log JSON
    # por request con más datos (duración, request_id). Sin esto quedarían dos líneas.
    logging.getLogger("uvicorn.access").disabled = True
