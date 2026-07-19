from __future__ import annotations

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