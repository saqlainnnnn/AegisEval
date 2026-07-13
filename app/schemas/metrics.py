from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class MetricType(str, Enum):
    """
    Supported evaluation metrics.
    """

    ACCURACY = "accuracy"
    PRECISION = "precision"
    RECALL = "recall"
    F1 = "f1"
    LATENCY = "latency"
    FAILURE_RATE = "failure_rate"
    GROUNDING_RATE = "grounding_rate"
    CITATION_ACCURACY = "citation_accuracy"
    HALLUCINATION_RATE = "hallucination_rate"


class MetricResult(BaseModel):
    """
    Result of a single evaluation metric.
    """

    model_config = ConfigDict(from_attributes=True)

    metric: MetricType

    value: float

    higher_is_better: bool = True

    metadata: dict[str, str] = Field(default_factory=dict)


class MetricSummary(BaseModel):
    """
    Collection of computed metrics for an evaluation run.
    """

    model_config = ConfigDict(from_attributes=True)

    metrics: list[MetricResult] = Field(default_factory=list)

    overall_score: float | None = None