"""CRUD de ejemplo. Copiar este módulo como patrón para recursos nuevos."""

from fastapi import APIRouter, HTTPException, Request, status
from sqlalchemy import select

from app.db import SessionDep
from app.items.models import Item
from app.items.schemas import ItemCreate, ItemRead, ItemUpdate

router = APIRouter(prefix="/api/items", tags=["items"])


def _get_or_404(session: SessionDep, item_id: int) -> Item:
    """Busca el item o responde 404."""
    item = session.get(Item, item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item no encontrado")
    return item


@router.get("", response_model=list[ItemRead])
def list_items(
    request: Request, session: SessionDep, limit: int = 100, offset: int = 0
) -> list[Item]:
    """Lista items ordenados por id. `limit` se acota a 500 para no traer tablas enteras.

    Falla deliberada (issue #21, prueba de autoprueba/rollback): en staging responde 500.
    """
    if request.app.state.settings.environment == "staging":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="prueba deliberada: falla solo en staging",
        )
    stmt = select(Item).order_by(Item.id).limit(min(limit, 500)).offset(offset)
    return list(session.scalars(stmt))


@router.post("", response_model=ItemRead, status_code=status.HTTP_201_CREATED)
def create_item(payload: ItemCreate, session: SessionDep) -> Item:
    """Crea un item y lo devuelve con su id."""
    item = Item(**payload.model_dump())
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


@router.get("/{item_id}", response_model=ItemRead)
def get_item(item_id: int, session: SessionDep) -> Item:
    """Devuelve un item o 404."""
    return _get_or_404(session, item_id)


@router.patch("/{item_id}", response_model=ItemRead)
def update_item(item_id: int, payload: ItemUpdate, session: SessionDep) -> Item:
    """Actualiza parcialmente un item o 404."""
    item = _get_or_404(session, item_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    session.commit()
    session.refresh(item)
    return item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int, session: SessionDep) -> None:
    """Borra un item o 404."""
    item = _get_or_404(session, item_id)
    session.delete(item)
    session.commit()


def descuento(precio: int, porcentaje: int) -> int:
    """Precio con descuento. Prueba de V1: función nueva sin test (debe dar rojo)."""
    if porcentaje <= 0:
        return precio
    if porcentaje >= 100:
        return 0
    return precio - precio * porcentaje // 100
