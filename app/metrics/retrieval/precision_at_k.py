from __future__ import annotations

from app.domain.enums import MetricType
from app.domain.evaluation import EvaluationResult
from app.domain.metrics import MetricResult
from app.metrics.retrieval.base import BaseRetrievalMetric


class PrecisionAtKMetric(BaseRetrievalMetric):
    """
    Computes Precision@K.

    Precision@K = Relevant Retrieved / Retrieved Documents
    """

    def compute(
        self,
        result: EvaluationResult,
    ) -> MetricResult:
        precisions: list[float] = []

        for sample in result.sample_results:
            if sample.prediction is None:
                precisions.append(0.0)
                continue

            expected_ids = {
                doc.id
                for doc in sample.question.expected_documents
            }

            retrieved = sample.prediction.retrieved_documents[: self.k]

            if not retrieved:
                precisions.append(0.0)
                continue

            retrieved_ids = {
                doc.id
                for doc in retrieved
            }

            hits = len(expected_ids & retrieved_ids)

            precisions.append(
                hits / len(retrieved)
            )

        score = (
            sum(precisions) / len(precisions)
            if precisions
            else 0.0
        )

        return MetricResult(
            metric=MetricType.PRECISION_AT_K,
            value=score,
            metadata={
                "k": self.k,
            },
        )