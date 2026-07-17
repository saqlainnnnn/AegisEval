from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from pydantic import Field

from app.domain.common import DomainModel, IdentifiableModel
from app.domain.dataset import Question
from app.domain.enums import EvaluationStatus, ModelType
from app.domain.prediction import Prediction


class ModelConfig(DomainModel):
    """
    Configuration of the evaluated AI system.
    """

    name: str

    version: str

    model_type: ModelType

    embedding_model: str | None = None

    prompt_version: str | None = None

    retriever: str | None = None

    chunk_size: int | None = None

    top_k: int | None = None

    metadata: dict[str, Any] = Field(default_factory=dict)


class EvaluationSampleResult(DomainModel):
    """
    Result of evaluating a single question.
    """

    question: Question

    prediction: Prediction | None = None

    status: EvaluationStatus = EvaluationStatus.SUCCESS

    latency_ms: float = 0.0

    error: str | None = None

    metadata: dict[str, Any] = Field(default_factory=dict)


class EvaluationResult(IdentifiableModel):
    """
    Represents a complete benchmark execution.
    """

    model: ModelConfig

    dataset_id: str

    sample_results: list[EvaluationSampleResult] = Field(
        default_factory=list,
    )

    started_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
    )

    finished_at: datetime | None = None

    duration_ms: float | None = None
