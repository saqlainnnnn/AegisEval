from __future__ import annotations

from app.api.models.evaluation import (
    EvaluationDetailResponse,
    EvaluationListItemResponse,
    EvaluationMetricResponse,
)


def to_evaluation_list_item(
    run,
) -> EvaluationListItemResponse:
    return EvaluationListItemResponse(
        evaluation_id=run.id,
        model_name=run.model.name,
        model_version=run.model.version,
        dataset_name=run.dataset.name,
        tracking_run_id=run.mlflow_run_id,
        started_at=run.started_at.isoformat(),
        finished_at=run.finished_at.isoformat(),
        duration_ms=run.duration_ms,
    )


def to_evaluation_detail(
    run,
) -> EvaluationDetailResponse:
    return EvaluationDetailResponse(
        evaluation_id=run.id,
        model_name=run.model.name,
        model_version=run.model.version,
        dataset_name=run.dataset.name,
        tracking_run_id=run.mlflow_run_id,
        started_at=run.started_at.isoformat(),
        finished_at=run.finished_at.isoformat(),
        duration_ms=run.duration_ms,
        metrics=[
            EvaluationMetricResponse(
                name=metric.metric_type,
                value=metric.value,
                higher_is_better=metric.higher_is_better,
            )
            for metric in run.metrics
        ],
    )