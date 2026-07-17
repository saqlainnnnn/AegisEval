from __future__ import annotations

from enum import Enum


class ModelType(str, Enum):
    """
    Supported AI system categories.
    """

    RAG = "rag"
    LLM = "llm"
    AGENT = "agent"
    VISION = "vision"
    MULTIMODAL = "multimodal"
    CUSTOM = "custom"


class EvaluationStatus(str, Enum):
    """
    Status of a single evaluation sample.
    """

    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


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


class RegressionStatus(str, Enum):
    """
    Outcome of a regression comparison.
    """

    PASSED = "passed"
    REGRESSION = "regression"


class ThresholdType(str, Enum):
    """
    Strategy used to evaluate an allowed metric change.
    """

    ABSOLUTE = "absolute"
    RELATIVE = "relative"
