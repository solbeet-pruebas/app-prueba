"""Esquemas Pydantic de entrada y salida de `items`."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ItemCreate(BaseModel):
    """Cuerpo de POST /api/items."""

    name: str = Field(min_length=1, max_length=200)
    description: str | None = None


class ItemUpdate(BaseModel):
    """Cuerpo de PATCH /api/items/{id}: solo se aplican los campos enviados."""

    name: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None


class ItemRead(BaseModel):
    """Respuesta de los endpoints de `items`."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    created_at: datetime
