from __future__ import annotations

from app.database.models import (
    EvaluationRunRecord,
    RegressionRunRecord,
)
from app.persistence.repositories import (
    EvaluationRunRepository,
    RegressionRunRepository,
)
from app.reports.builder import ReportBuilder
from app.reports.models import (
    EvaluationReport,
    RegressionReport,
)


class ReportService:
    """
    Builds reports from persisted evaluation and
    regression runs.
    """

    def __init__(
        self,
        *,
        evaluation_repository: EvaluationRunRepository,
        regression_repository: RegressionRunRepository,
        builder: ReportBuilder | None = None,
    ) -> None:
        self._evaluation_repository = evaluation_repository
        self._regression_repository = regression_repository
        self._builder = builder or ReportBuilder()

    def build_evaluation_report(
        self,
        run_id: str,
    ) -> EvaluationReport:
        run: EvaluationRunRecord | None = (
            self._evaluation_repository.get(run_id)
        )

        if run is None:
            raise ValueError(
                f"Evaluation run '{run_id}' not found."
            )

        return self._builder.build_evaluation_report(run)

    def build_regression_report(
        self,
        regression_id: str,
    ) -> RegressionReport:
        run: RegressionRunRecord | None = (
            self._regression_repository.get(regression_id)
        )

        if run is None:
            raise ValueError(
                f"Regression run '{regression_id}' not found."
            )

        return self._builder.build_regression_report(run)