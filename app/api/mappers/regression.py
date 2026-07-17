from __future__ import annotations

from app.api.models.regression import (
    RegressionDetailResponse,
    RegressionListItemResponse,
    RegressionMetricResponse,
)


def to_regression_list_item(
    run,
) -> RegressionListItemResponse:
    return RegressionListItemResponse(
        regression_id=run.id,
        baseline_evaluation_id=run.baseline_evaluation_id,
        candidate_evaluation_id=run.candidate_evaluation_id,
        status=run.status,
        started_at=run.started_at.isoformat(),
        finished_at=run.finished_at.isoformat(),
        duration_ms=run.duration_ms,
    )


def to_regression_detail(
    run,
) -> RegressionDetailResponse:
    return RegressionDetailResponse(
        regression_id=run.id,
        baseline_evaluation_id=run.baseline_evaluation_id,
        candidate_evaluation_id=run.candidate_evaluation_id,
        status=run.status,
        started_at=run.started_at.isoformat(),
        finished_at=run.finished_at.isoformat(),
        duration_ms=run.duration_ms,
        metrics=[
            RegressionMetricResponse(
                name=metric.metric_type,
                baseline_value=metric.baseline_value,
                candidate_value=metric.candidate_value,
                delta=metric.delta,
                threshold=metric.threshold,
                passed=metric.passed,
            )
            for metric in run.metrics
        ],
    )