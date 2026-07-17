from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field

from app.domain.enums import ModelType


class EvaluationQuestionRequest(BaseModel):
    """
    A single evaluation question submitted through the API.
    """

    question: str = Field(
        min_length=1,
    )

    expected_answer: str = Field(
        min_length=1,
    )


class EvaluationDatasetRequest(BaseModel):
    """
    Dataset submitted for evaluation.
    """

    name: str = Field(
        min_length=1,
    )

    description: str = ""

    version: str | None = None

    questions: list[EvaluationQuestionRequest] = Field(
        min_length=1,
    )


class EvaluationModelRequest(BaseModel):
    """
    Configuration for the system being evaluated.
    """

    name: str = Field(
        min_length=1,
    )

    version: str = Field(
        min_length=1,
    )

    model_type: ModelType

    embedding_model: str | None = None
    prompt_version: str | None = None
    retriever: str | None = None
    chunk_size: int | None = Field(
        default=None,
        gt=0,
    )
    top_k: int | None = Field(
        default=None,
        gt=0,
    )


class CreateEvaluationRequest(BaseModel):
    """
    Request to execute a new evaluation.
    """

    model: EvaluationModelRequest
    dataset: EvaluationDatasetRequest


class EvaluationMetricResponse(BaseModel):
    """
    Metric returned by an evaluation.
    """

    name: str
    value: float
    higher_is_better: bool


class CreateEvaluationResponse(BaseModel):
    """
    Response returned after an evaluation completes.
    """

    evaluation_id: UUID
    dataset_id: UUID
    tracking_run_id: str | None

    model_name: str
    model_version: str

    metrics: list[EvaluationMetricResponse]


class EvaluationListItemResponse(BaseModel):
    """
    Summary of a persisted evaluation run.
    """

    evaluation_id: str
    model_name: str
    model_version: str
    dataset_name: str
    tracking_run_id: str | None
    started_at: str
    finished_at: str
    duration_ms: float


class EvaluationDetailResponse(EvaluationListItemResponse):
    """
    Detailed persisted evaluation run.
    """

    metrics: list[EvaluationMetricResponse]
