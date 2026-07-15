from __future__ import annotations

from typing import Any

from sqlalchemy import Boolean, Float, ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class MetricRecord(Base):
    """
    Persisted metric produced by an evaluation run.
    """

    __tablename__ = "metrics"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    evaluation_run_id: Mapped[str] = mapped_column(
        ForeignKey("evaluation_runs.id"),
        nullable=False,
        index=True,
    )

    metric_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    value: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    higher_is_better: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
    )

    metric_metadata: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )

    evaluation_run: Mapped[
        "EvaluationRunRecord"
    ] = relationship(
        back_populates="metrics",
    )