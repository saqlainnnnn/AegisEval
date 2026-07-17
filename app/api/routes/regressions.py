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

from app.api.mappers.regression import (
    to_regression_response_from_domain,
    to_regression_response_from_record,
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

    return to_regression_response_from_domain(
    regression_id=service_result.regression_id,
    result=service_result.result,
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

    return to_regression_response_from_record(record)
