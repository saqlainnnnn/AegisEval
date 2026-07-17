from __future__ import annotations

from pydantic import BaseModel, Field, model_validator

from app.domain.enums import (
    MetricType,
    RegressionStatus,
    ThresholdType,
)


class RegressionThreshold(BaseModel):
    """
    Defines the maximum tolerated degradation for a metric.
    """

    metric: MetricType
    threshold_type: ThresholdType

    value: float = Field(
        ge=0,
    )


class MetricComparison(BaseModel):
    """
    Comparison of one metric between a baseline and
    candidate evaluation run.
    """

    metric: MetricType

    baseline_value: float
    candidate_value: float

    absolute_change: float
    relative_change: float | None

    threshold: RegressionThreshold

    status: RegressionStatus


class RegressionResult(BaseModel):
    """
    Complete result of comparing two evaluation runs.
    """

    baseline_run_id: str = Field(
        min_length=1,
    )

    candidate_run_id: str = Field(
        min_length=1,
    )

    status: RegressionStatus

    comparisons: list[MetricComparison] = Field(
        min_length=1,
    )

    @model_validator(mode="after")
    def validate_status(
        self,
    ) -> RegressionResult:
        """
        Ensure the overall status agrees with the
        individual metric comparison statuses.
        """

        has_regression = any(
            comparison.status == RegressionStatus.REGRESSION
            for comparison in self.comparisons
        )

        expected_status = (
            RegressionStatus.REGRESSION if has_regression else RegressionStatus.PASSED
        )

        if self.status != expected_status:
            raise ValueError(
                "Regression result status does not " "match comparison statuses."
            )

        return self
