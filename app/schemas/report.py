from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import IdentifiableModel
from app.schemas.metrics import MetricSummary


class ComparisonResult(BaseModel):
    """
    Comparison between two evaluation runs.
    """

    model_config = ConfigDict(from_attributes=True)

    baseline_run_id: str

    current_run_id: str

    improvements: dict[str, float] = Field(default_factory=dict)

    regressions: dict[str, float] = Field(default_factory=dict)


class Report(IdentifiableModel):
    """
    Evaluation report generated after a benchmark run.
    """

    title: str

    summary: str

    metrics: MetricSummary

    comparison: ComparisonResult | None = None