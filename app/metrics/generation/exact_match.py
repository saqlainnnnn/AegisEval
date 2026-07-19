from __future__ import annotations

from app.domain.enums import MetricType
from app.domain.evaluation import EvaluationResult
from app.domain.metrics import MetricResult
from app.metrics.generation.base import BaseGenerationMetric


class ExactMatchMetric(BaseGenerationMetric):
    """
    Computes Exact Match (EM).
    """

    def compute(
        self,
        result: EvaluationResult,
    ) -> MetricResult:
        matches = 0

        for sample in result.sample_results:
            if (
                self._normalized_prediction(sample)
                == self._normalized_reference(sample)
            ):
                matches += 1

        score = (
            matches / len(result.sample_results)
            if result.sample_results
            else 0.0
        )

        return MetricResult(
            metric=MetricType.EXACT_MATCH,
            value=score,
        )