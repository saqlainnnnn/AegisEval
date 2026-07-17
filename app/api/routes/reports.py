from __future__ import annotations

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from app.api.dependencies import (
    get_report_service,
)
from app.reports.models import (
    EvaluationReport,
    RegressionReport,
)
from app.services.report import ReportService


router = APIRouter(
    prefix="/reports",
    tags=["Reports"],
)


@router.get(
    "/evaluations/{evaluation_id}",
    response_model=EvaluationReport,
)
def get_evaluation_report(
    evaluation_id: str,
    report_service: ReportService = Depends(
        get_report_service,
    ),
) -> EvaluationReport:
    """
    Build a report for a persisted evaluation run.
    """

    try:
        return report_service.build_evaluation_report(
            evaluation_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.get(
    "/regressions/{regression_id}",
    response_model=RegressionReport,
)
def get_regression_report(
    regression_id: str,
    report_service: ReportService = Depends(
        get_report_service,
    ),
) -> RegressionReport:
    """
    Build a report for a persisted regression run.
    """

    try:
        return report_service.build_regression_report(
            regression_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc