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

    # Classification Metrics
    ACCURACY = "accuracy"
    PRECISION = "precision"
    RECALL = "recall"
    

    # Performance Metrics
    LATENCY = "latency"
    FAILURE_RATE = "failure_rate"

    # Retrieval Metrics
    RECALL_AT_K = "recall_at_k"
    PRECISION_AT_K = "precision_at_k"
    HIT_RATE_AT_K = "hit_rate_at_k"
    MRR = "mrr"
    MAP = "map"
    NDCG = "ndcg"

    # RAG Metrics
    GROUNDING_RATE = "grounding_rate"
    CITATION_ACCURACY = "citation_accuracy"
    HALLUCINATION_RATE = "hallucination_rate"

    #GENERATION Metrics
    EXACT_MATCH = "exact_match"
    F1 = "f1"
    BLEU = "bleu"
    ROUGE_L = "rouge_l"

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
