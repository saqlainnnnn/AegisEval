from __future__ import annotations

from app.domain.enums import MetricType
from app.domain.evaluation import EvaluationResult
from app.domain.metrics import MetricResult
from app.metrics.base import BaseMetric


class LatencyMetric(BaseMetric):
    """
    Computes average latency in milliseconds.
    """

    def compute(
        self,
        result: EvaluationResult,
    ) -> MetricResult:

        if not result.sample_results:
            return MetricResult(
                metric=MetricType.LATENCY,
                value=0.0,
            )

        latencies = [
            sample.latency_ms
            for sample in result.sample_results
        ]

        average = sum(latencies) / len(latencies)

        return MetricResult(
            metric=MetricType.LATENCY,
            value=average,
            higher_is_better=False,
            metadata={
                "min": min(latencies),
                "max": max(latencies),
                "samples": len(latencies),
            },
        )