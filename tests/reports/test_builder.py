from __future__ import annotations

from datetime import UTC, datetime

from app.database.models import (
    DatasetRecord,
    EvaluationRunRecord,
    MetricRecord,
    ModelRecord,
    RegressionMetricRecord,
    RegressionRunRecord,
)
from app.domain.enums import (
    MetricType,
    ModelType,
    RegressionStatus,
)
from app.reports.builder import ReportBuilder


def test_build_evaluation_report() -> None:
    builder = ReportBuilder()

    model = ModelRecord(
        id="model-id",
        name="GPT",
        version="1.0",
        model_type=ModelType.LLM.value,
        embedding_model="bge-small",
        prompt_version="v1",
        retriever="hybrid",
        chunk_size=512,
        top_k=5,
        created_at=datetime.now(UTC),
    )

    dataset = DatasetRecord(
        id="dataset-id",
        name="Medical QA",
        description="Demo dataset",
        version="1.0",
        created_at=datetime.now(UTC),
    )

    run = EvaluationRunRecord(
        id="run-id",
        model=model,
        dataset=dataset,
        mlflow_run_id="mlflow-123",
        started_at=datetime.now(UTC),
        finished_at=datetime.now(UTC),
        duration_ms=123.4,
    )

    run.metrics.extend(
        [
            MetricRecord(
                metric_type=MetricType.ACCURACY.value,
                value=0.95,
                higher_is_better=True,
                metric_metadata={},
            ),
            MetricRecord(
                metric_type=MetricType.RECALL.value,
                value=0.90,
                higher_is_better=True,
                metric_metadata={},
            ),
        ]
    )

    report = builder.build_evaluation_report(run)

    assert report.metadata.evaluation_run_id == "run-id"

    assert report.model.name == "GPT"
    assert report.model.chunk_size == 512
    assert report.model.top_k == 5

    assert report.dataset.name == "Medical QA"

    assert report.summary.total_metrics == 2

    assert len(report.metrics) == 2

    assert report.metrics[0].metric == MetricType.ACCURACY

    assert report.metrics[1].metric == MetricType.RECALL


def test_build_regression_report() -> None:
    builder = ReportBuilder()

    regression = RegressionRunRecord(
        id="regression-id",
        baseline_run_id="baseline",
        candidate_run_id="candidate",
        status=RegressionStatus.PASSED.value,
    )

    regression.comparisons.append(
        RegressionMetricRecord(
            metric_type=MetricType.ACCURACY.value,
            baseline_value=0.91,
            candidate_value=0.94,
            absolute_change=0.03,
            relative_change=0.033,
            threshold_type="absolute",
            threshold_value=0.02,
            status=RegressionStatus.PASSED.value,
        )
    )

    report = builder.build_regression_report(
        regression
    )

    assert report.baseline_run_id == "baseline"

    assert report.candidate_run_id == "candidate"

    assert report.status == RegressionStatus.PASSED

    assert len(report.comparisons) == 1

    metric = report.comparisons[0]

    assert metric.metric == MetricType.ACCURACY

    assert metric.baseline_value == 0.91

    assert metric.candidate_value == 0.94

    assert metric.status == RegressionStatus.PASSED