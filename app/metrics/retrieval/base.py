from __future__ import annotations

from app.domain.evaluation import EvaluationSampleResult
from app.metrics.base import BaseMetric


class BaseRetrievalMetric(BaseMetric):
    """
    Base class for retrieval metrics evaluated at a cutoff K.
    """

    def __init__(
        self,
        k: int = 5,
    ) -> None:
        self.k = k

    def _expected_ids(
        self,
        sample: EvaluationSampleResult,
    ) -> set[str]:
        return {
            doc.id
            for doc in sample.question.expected_documents
        }

    def _retrieved_ids(
        self,
        sample: EvaluationSampleResult,
    ) -> list[str]:
        if sample.prediction is None:
            return []

        return [
            doc.id
            for doc in sample.prediction.retrieved_documents[: self.k]
        ]