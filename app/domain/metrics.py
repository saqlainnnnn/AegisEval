from __future__ import annotations

from typing import Any

from pydantic import Field

from app.domain.common import DomainModel
from app.domain.enums import MetricType


class MetricResult(DomainModel):
    """
    Represents the value of a single evaluation metric.
    """

    metric: MetricType

    value: float

    higher_is_better: bool = True

    metadata: dict[str, Any] = Field(default_factory=dict)


class MetricSummary(DomainModel):
    """
    Collection of metric results for an evaluation run.
    """

    metrics: dict[MetricType, MetricResult] = Field(
        default_factory=dict
    )

    overall_score: float | None = None