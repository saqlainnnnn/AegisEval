from __future__ import annotations

from datetime import UTC, datetime

from app.adapters.base import BaseAdapter
from app.benchmark.executor import EvaluationExecutor
from app.domain.dataset import Dataset
from app.domain.evaluation import EvaluationResult


class BenchmarkRunner:
    """
    Executes an evaluation over an entire dataset.
    """

    def __init__(
        self,
        adapter: BaseAdapter,
    ) -> None:
        self._executor = EvaluationExecutor(adapter)
        self._adapter = adapter

    def run(
        self,
        dataset: Dataset,
    ) -> EvaluationResult:
        """
        Execute the benchmark.
        """

        started_at = datetime.now(UTC)

        sample_results = [
            self._executor.execute(question)
            for question in dataset.questions
        ]

        finished_at = datetime.now(UTC)

        duration_ms = (
            finished_at - started_at
        ).total_seconds() * 1000

        return EvaluationResult(
            model=self._adapter.config,
            dataset_id=str(dataset.id),
            sample_results=sample_results,
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=duration_ms,
        )