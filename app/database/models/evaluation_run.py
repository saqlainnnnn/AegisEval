from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class EvaluationRunRecord(Base):
    """
    Persisted evaluation run.
    """

    __tablename__ = "evaluation_runs"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
    )

    model_id: Mapped[str] = mapped_column(
        ForeignKey("models.id"),
        nullable=False,
        index=True,
    )

    dataset_id: Mapped[str] = mapped_column(
        ForeignKey("datasets.id"),
        nullable=False,
        index=True,
    )

    mlflow_run_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        index=True,
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    finished_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    duration_ms: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    model: Mapped["ModelRecord"] = relationship(
        back_populates="evaluation_runs",
    )

    dataset: Mapped["DatasetRecord"] = relationship(
        back_populates="evaluation_runs",
    )

    metrics: Mapped[list["MetricRecord"]] = relationship(
        back_populates="evaluation_run",
        cascade="all, delete-orphan",
    )
