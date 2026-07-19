from __future__ import annotations

from app.domain.enums import MetricType
from app.domain.evaluation import EvaluationResult
from app.domain.metrics import MetricResult
from app.metrics.retrieval.base import BaseRetrievalMetric


class RecallMetric(BaseRetrievalMetric):
    """
    Computes Recall@K.

    Recall@K = Relevant Retrieved / Total Relevant
    """

    def compute(
        self,
        result: EvaluationResult,
    ) -> MetricResult:
        recalls: list[float] = []

        for sample in result.sample_results:
            if sample.prediction is None:
                recalls.append(0.0)
                continue

            expected_ids = {
                doc.id
                for doc in sample.question.expected_documents
            }

            retrieved_ids = {
                doc.id
                for doc in sample.prediction.retrieved_documents[: self.k]
            }

            if not expected_ids:
                recalls.append(1.0)
                continue

            hits = len(expected_ids & retrieved_ids)

            recalls.append(hits / len(expected_ids))

        score = (
            sum(recalls) / len(recalls)
            if recalls
            else 0.0
        )

        return MetricResult(
            metric=MetricType.RECALL_AT_K,
            value=score,
            metadata={
                "k": self.k,
            },
        )