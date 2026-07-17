from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class ModelRecord(Base):
    """
    Persisted AI model configuration.
    """

    __tablename__ = "models"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    version: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    model_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    embedding_model: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    prompt_version: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    retriever: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    chunk_size: Mapped[int | None] = mapped_column(
        nullable=True,
    )

    top_k: Mapped[int | None] = mapped_column(
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    evaluation_runs: Mapped[list["EvaluationRunRecord"]] = relationship(
        back_populates="model",
    )
