from __future__ import annotations

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from app.api.dependencies import (
    get_regression_run_repository,
    get_regression_service,
)
from app.api.models.regression import (
    CreateRegressionRequest,
    RegressionMetricResponse,
    RegressionResponse,
)
from app.domain.regression import (
    RegressionThreshold,
)
from app.persistence.repositories import (
    RegressionRunRepository,
)
from app.services.regression import (
    RegressionService,
)

router = APIRouter(
    prefix="/regressions",
    tags=["regressions"],
)


@router.post(
    "",
    response_model=RegressionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_regression(
    request: CreateRegressionRequest,
    service: RegressionService = Depends(get_regression_service),
) -> RegressionResponse:
    """
    Compare two persisted evaluation runs.
    """

    thresholds = [
        RegressionThreshold(
            metric=threshold.metric,
            threshold_type=(threshold.threshold_type),
            value=threshold.value,
        )
        for threshold in request.thresholds
    ]

    try:
        service_result = service.compare(
            baseline_run_id=(request.baseline_run_id),
            candidate_run_id=(request.candidate_run_id),
            thresholds=thresholds,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=(status.HTTP_404_NOT_FOUND),
            detail=str(error),
        ) from error

    result = service_result.result

    return RegressionResponse(
        regression_id=(service_result.regression_id),
        baseline_run_id=(result.baseline_run_id),
        candidate_run_id=(result.candidate_run_id),
        status=result.status,
        comparisons=[
            RegressionMetricResponse(
                metric=comparison.metric,
                baseline_value=(comparison.baseline_value),
                candidate_value=(comparison.candidate_value),
                absolute_change=(comparison.absolute_change),
                relative_change=(comparison.relative_change),
                threshold_type=(comparison.threshold.threshold_type),
                threshold_value=(comparison.threshold.value),
                status=comparison.status,
            )
            for comparison in result.comparisons
        ],
    )


@router.get(
    "/{regression_id}",
    response_model=RegressionResponse,
)
def get_regression(
    regression_id: str,
    repository: RegressionRunRepository = Depends(get_regression_run_repository),
) -> RegressionResponse:
    """
    Return one persisted regression result.
    """

    record = repository.get(regression_id)

    if record is None:
        raise HTTPException(
            status_code=(status.HTTP_404_NOT_FOUND),
            detail="Regression not found",
        )

    return RegressionResponse(
        regression_id=record.id,
        baseline_run_id=(record.baseline_run_id),
        candidate_run_id=(record.candidate_run_id),
        status=record.status,
        comparisons=[
            RegressionMetricResponse(
                metric=(comparison.metric_type),
                baseline_value=(comparison.baseline_value),
                candidate_value=(comparison.candidate_value),
                absolute_change=(comparison.absolute_change),
                relative_change=(comparison.relative_change),
                threshold_type=(comparison.threshold_type),
                threshold_value=(comparison.threshold_value),
                status=comparison.status,
            )
            for comparison in record.comparisons
        ],
    )
