from __future__ import annotations

from app.domain.evaluation import EvaluationResult
from app.domain.metrics import MetricSummary
from app.metrics.base import BaseMetric


class MetricsEngine:
    """
    Executes a collection of evaluation metrics.
    """

    def __init__(
        self,
        metrics: list[BaseMetric],
    ) -> None:
        self._metrics = metrics

    def compute(
        self,
        result: EvaluationResult,
    ) -> MetricSummary:
        """
        Compute all registered metrics.
        """

        summary = MetricSummary()

        for metric in self._metrics:

            metric_result = metric.compute(result)

            summary.metrics[metric_result.metric] = metric_result

        return summary
