from __future__ import annotations

from dataclasses import dataclass

from app.benchmark.runner import BenchmarkRunner
from app.domain.dataset import Dataset
from app.domain.evaluation import EvaluationResult
from app.domain.metrics import MetricSummary
from app.metrics.engine import MetricsEngine
from app.tracking.base import BaseExperimentTracker


@dataclass(frozen=True)
class EvaluationServiceResult:
    """
    Result produced by the complete evaluation workflow.
    """

    evaluation: EvaluationResult
    metrics: MetricSummary
    tracking_run_id: str | None = None


class EvaluationService:
    """
    Coordinates benchmark execution, metric computation,
    and experiment tracking.
    """

    def __init__(
        self,
        runner: BenchmarkRunner,
        metrics_engine: MetricsEngine,
        tracker: BaseExperimentTracker | None = None,
    ) -> None:
        self._runner = runner
        self._metrics_engine = metrics_engine
        self._tracker = tracker

    def evaluate(
        self,
        dataset: Dataset,
    ) -> EvaluationServiceResult:
        """
        Execute the complete evaluation workflow.
        """

        evaluation = self._runner.run(dataset)

        metrics = self._metrics_engine.compute(evaluation)

        tracking_run_id: str | None = None

        if self._tracker is not None:
            with self._tracker.start_run(evaluation) as tracking_run:
                tracking_run_id = tracking_run.run_id

                tracking_run.log_metrics(metrics)

                tracking_run.log_evaluation()

        return EvaluationServiceResult(
            evaluation=evaluation,
            metrics=metrics,
            tracking_run_id=tracking_run_id,
        )
