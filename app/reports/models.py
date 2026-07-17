from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from app.domain.enums import (
    MetricType,
    ModelType,
    RegressionStatus,
)


class ReportMetadata(BaseModel):
    """
    Metadata describing a generated report.
    """

    report_id: UUID = Field(default_factory=uuid4)

    generated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC)
    )

    generated_by: str = "AegisEval"

    version: str = "1.0"

    evaluation_run_id: str

    mlflow_run_id: str | None = None


class MetricReport(BaseModel):
    """
    Report representation of a single metric.
    """

    metric: MetricType

    value: float

    higher_is_better: bool

    metadata: dict[str, Any] = Field(
        default_factory=dict
    )


class SummaryReport(BaseModel):
    """
    High-level evaluation summary.
    """

    total_metrics: int

    overall_score: float | None = None

    evaluation_duration_ms: float

    started_at: datetime

    finished_at: datetime

    evaluation_status: str = "completed"


class ModelInformation(BaseModel):
    """
    Information describing the evaluated model.
    """

    name: str

    version: str

    model_type: ModelType

    embedding_model: str | None = None

    prompt_version: str | None = None

    retriever: str | None = None

    chunk_size: int | None = None

    top_k: int | None = None


class DatasetInformation(BaseModel):
    """
    Information describing the evaluated dataset.
    """

    dataset_id: str

    name: str

    description: str

    version: str | None = None


class EvaluationReport(BaseModel):
    """
    Complete evaluation report.
    """

    metadata: ReportMetadata

    model: ModelInformation

    dataset: DatasetInformation

    summary: SummaryReport

    metrics: list[MetricReport] = Field(
        default_factory=list
    )


class RegressionMetricReport(BaseModel):
    """
    Comparison between baseline and candidate
    for a single metric.
    """

    metric: MetricType

    baseline_value: float

    candidate_value: float

    absolute_change: float

    relative_change: float | None

    status: RegressionStatus


class RegressionReport(BaseModel):
    """
    Complete regression report.
    """

    metadata: ReportMetadata

    baseline_run_id: str

    candidate_run_id: str

    status: RegressionStatus

    comparisons: list[
        RegressionMetricReport
    ] = Field(default_factory=list)