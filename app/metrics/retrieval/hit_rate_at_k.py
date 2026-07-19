from __future__ import annotations

from app.domain.enums import MetricType
from app.domain.evaluation import EvaluationResult
from app.domain.metrics import MetricResult
from app.metrics.retrieval.base import BaseRetrievalMetric


class HitRateAtKMetric(BaseRetrievalMetric):
    """
    Computes Hit Rate@K.

    Hit Rate@K = 1 if at least one relevant document
    appears in the top K results, otherwise 0.
    """

    def compute(
        self,
        result: EvaluationResult,
    ) -> MetricResult:
        hits: list[float] = []

        for sample in result.sample_results:
            expected = self._expected_ids(sample)
            retrieved = self._retrieved_ids(sample)

            if expected.intersection(retrieved):
                hits.append(1.0)
            else:
                hits.append(0.0)

        score = (
            sum(hits) / len(hits)
            if hits
            else 0.0
        )

        return MetricResult(
            metric=MetricType.HIT_RATE_AT_K,
            value=score,
            metadata={
                "k": self.k,
            },
        )