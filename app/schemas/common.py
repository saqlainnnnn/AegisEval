from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class TimestampedModel(BaseModel):
    """
    Base model containing creation and update timestamps.
    """

    model_config = ConfigDict(from_attributes=True)

    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class IdentifiableModel(TimestampedModel):
    """
    Base model containing a unique identifier.
    """

    id: UUID = Field(default_factory=uuid4)


class APIResponse(BaseModel):
    """
    Standard API response model.
    """

    success: bool
    message: str
    data: dict | list | None = None