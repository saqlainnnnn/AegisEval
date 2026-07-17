from __future__ import annotations

from time import perf_counter

from app.adapters.base import BaseAdapter
from app.domain.dataset import Question
from app.domain.enums import EvaluationStatus
from app.domain.evaluation import EvaluationSampleResult


class EvaluationExecutor:
    """
    Executes a single evaluation sample.
    """

    def __init__(
        self,
        adapter: BaseAdapter,
    ) -> None:
        self._adapter = adapter

    def execute(
        self,
        question: Question,
    ) -> EvaluationSampleResult:
        """
        Evaluate a single question.
        """

        start = perf_counter()

        try:
            prediction = self._adapter.evaluate(question)

            latency_ms = (perf_counter() - start) * 1000

            return EvaluationSampleResult(
                question=question,
                prediction=prediction,
                status=EvaluationStatus.SUCCESS,
                latency_ms=latency_ms,
            )

        except Exception as exc:

            latency_ms = (perf_counter() - start) * 1000

            return EvaluationSampleResult(
                question=question,
                prediction=None,
                status=EvaluationStatus.FAILED,
                latency_ms=latency_ms,
                error=str(exc),
            )
