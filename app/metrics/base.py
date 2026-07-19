from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.evaluation import EvaluationResult
from app.domain.metrics import MetricResult


class BaseMetric(ABC):
    """
    Base interface for all evaluation metrics.
    """

    @abstractmethod
    def compute(
        self,
        result: EvaluationResult,
    ) -> MetricResult:
        """
        Compute a metric for an evaluation result.
        """
        raise NotImplementedError