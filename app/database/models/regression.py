from __future__ import annotations

from uuid import uuid4

from sqlalchemy import Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class RegressionRunRecord(Base):
    """
    Persisted regression comparison between two
    evaluation runs.
    """

    __tablename__ = "regression_runs"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    baseline_run_id: Mapped[str] = mapped_column(
        ForeignKey("evaluation_runs.id"),
        nullable=False,
        index=True,
    )

    candidate_run_id: Mapped[str] = mapped_column(
        ForeignKey("evaluation_runs.id"),
        nullable=False,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    comparisons: Mapped[
        list["RegressionMetricRecord"]
    ] = relationship(
        back_populates="regression_run",
        cascade="all, delete-orphan",
    )


class RegressionMetricRecord(Base):
    """
    Persisted comparison for one metric.
    """

    __tablename__ = "regression_metrics"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    regression_run_id: Mapped[str] = mapped_column(
        ForeignKey("regression_runs.id"),
        nullable=False,
        index=True,
    )

    metric_type: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    baseline_value: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    candidate_value: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    absolute_change: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    relative_change: Mapped[
        float | None
    ] = mapped_column(
        Float,
        nullable=True,
    )

    threshold_type: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    threshold_value: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    regression_run: Mapped[
        RegressionRunRecord
    ] = relationship(
        back_populates="comparisons"
    )