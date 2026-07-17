from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class DomainModel(BaseModel):
    """
    Base class for all domain models.
    """

    model_config = ConfigDict(
        from_attributes=True,
        extra="forbid",
    )


class TimestampedModel(DomainModel):
    """
    Base model that stores creation and update timestamps.
    """

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
    )

    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
    )


class IdentifiableModel(TimestampedModel):
    """
    Base model with a unique identifier.
    """

    id: UUID = Field(
        default_factory=uuid4,
    )
