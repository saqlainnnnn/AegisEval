from __future__ import annotations

from dataclasses import dataclass

from app.domain.enums import MetricType
from app.domain.metrics import (
    MetricResult,
    MetricSummary,
)
from app.domain.regression import (
    RegressionResult,
    RegressionThreshold,
)
from app.persistence.repositories import (
    EvaluationRunRepository,
    RegressionRunRepository,
)
from app.regression.engine import RegressionEngine


@dataclass(frozen=True)
class RegressionServiceResult:
    """
    Result returned after a regression comparison
    has been executed and persisted.
    """

    regression_id: str
    result: RegressionResult


class RegressionService:
    """
    Orchestrates regression comparisons between
    persisted evaluation runs.
    """

    def __init__(
        self,
        *,
        evaluation_repository: EvaluationRunRepository,
        regression_repository: RegressionRunRepository,
        regression_engine: RegressionEngine,
    ) -> None:
        self._evaluation_repository = evaluation_repository

        self._regression_repository = regression_repository

        self._regression_engine = regression_engine

    def compare(
        self,
        *,
        baseline_run_id: str,
        candidate_run_id: str,
        thresholds: list[RegressionThreshold],
    ) -> RegressionServiceResult:
        """
        Compare two persisted evaluation runs,
        persist the result, and return its ID.
        """

        baseline_run = self._evaluation_repository.get(baseline_run_id)

        if baseline_run is None:
            raise ValueError(
                "Baseline evaluation run " f"{baseline_run_id} was not found."
            )

        candidate_run = self._evaluation_repository.get(candidate_run_id)

        if candidate_run is None:
            raise ValueError(
                "Candidate evaluation run " f"{candidate_run_id} was not found."
            )

        baseline_summary = self._build_metric_summary(baseline_run.metrics)

        candidate_summary = self._build_metric_summary(candidate_run.metrics)

        result = self._regression_engine.compare(
            baseline_run_id=baseline_run_id,
            candidate_run_id=candidate_run_id,
            baseline=baseline_summary,
            candidate=candidate_summary,
            thresholds=thresholds,
        )

        stored_record = self._regression_repository.save(result)

        return RegressionServiceResult(
            regression_id=stored_record.id,
            result=result,
        )

    @staticmethod
    def _build_metric_summary(
        metric_records,
    ) -> MetricSummary:
        """
        Reconstruct a domain metric summary from
        persisted metric records.
        """

        metrics = {
            MetricType(record.metric_type): MetricResult(
                metric=MetricType(record.metric_type),
                value=record.value,
                higher_is_better=(record.higher_is_better),
            )
            for record in metric_records
        }

        return MetricSummary(metrics=metrics)
