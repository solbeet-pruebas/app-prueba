"""GET /api/canario: dice que la API responde y qué versión es, en una sola llamada.

No toca la base ni requiere autenticación. La versión es la de `GET /api/version`
(se reutiliza `leer_version`), así no se mantiene a mano en otro lugar.
"""

from fastapi import APIRouter

from app.api.version import leer_version

router = APIRouter(prefix="/api", tags=["canario"])


@router.get("/canario")
def canario() -> dict[str, bool | str]:
    """Confirma que la API está viva y devuelve la versión que responde."""
    return {"ok": True, "version": leer_version()}
