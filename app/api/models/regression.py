from __future__ import annotations

from pydantic import BaseModel, Field

from app.domain.enums import (
    MetricType,
    RegressionStatus,
    ThresholdType,
)


class RegressionThresholdRequest(BaseModel):
    """
    Threshold configuration for one metric.
    """

    metric: MetricType

    threshold_type: ThresholdType

    value: float = Field(
        ge=0,
    )


class CreateRegressionRequest(BaseModel):
    """
    Request to compare two evaluation runs.
    """

    baseline_run_id: str = Field(
        min_length=1,
    )

    candidate_run_id: str = Field(
        min_length=1,
    )

    thresholds: list[RegressionThresholdRequest] = Field(
        min_length=1,
    )


class RegressionMetricResponse(BaseModel):
    """
    Comparison result for one metric.
    """

    metric: MetricType

    baseline_value: float
    candidate_value: float

    absolute_change: float
    relative_change: float | None

    threshold_type: ThresholdType
    threshold_value: float

    status: RegressionStatus


class RegressionResponse(BaseModel):
    """
    Complete persisted regression result.
    """

    regression_id: str

    baseline_run_id: str
    candidate_run_id: str

    status: RegressionStatus

    comparisons: list[RegressionMetricResponse]
