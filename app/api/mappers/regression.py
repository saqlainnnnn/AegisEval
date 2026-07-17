from __future__ import annotations

from app.api.models.regression import (
    RegressionMetricResponse,
    RegressionResponse,
)
from app.domain.regression import RegressionResult


def to_regression_response_from_domain(
    *,
    regression_id: str,
    result: RegressionResult,
) -> RegressionResponse:
    """
    Convert a domain RegressionResult into an API response.
    Used immediately after executing a regression.
    """

    return RegressionResponse(
        regression_id=regression_id,
        baseline_run_id=result.baseline_run_id,
        candidate_run_id=result.candidate_run_id,
        status=result.status,
        comparisons=[
            RegressionMetricResponse(
                metric=comparison.metric,
                baseline_value=comparison.baseline_value,
                candidate_value=comparison.candidate_value,
                absolute_change=comparison.absolute_change,
                relative_change=comparison.relative_change,
                threshold_type=comparison.threshold.threshold_type,
                threshold_value=comparison.threshold.value,
                status=comparison.status,
            )
            for comparison in result.comparisons
        ],
    )


def to_regression_response_from_record(
    record,
) -> RegressionResponse:
    """
    Convert a persisted regression record into an API response.
    Used when retrieving an existing regression.
    """

    return RegressionResponse(
        regression_id=record.id,
        baseline_run_id=record.baseline_run_id,
        candidate_run_id=record.candidate_run_id,
        status=record.status,
        comparisons=[
            RegressionMetricResponse(
                metric=comparison.metric_type,
                baseline_value=comparison.baseline_value,
                candidate_value=comparison.candidate_value,
                absolute_change=comparison.absolute_change,
                relative_change=comparison.relative_change,
                threshold_type=comparison.threshold_type,
                threshold_value=comparison.threshold_value,
                status=comparison.status,
            )
            for comparison in record.comparisons
        ],
    )