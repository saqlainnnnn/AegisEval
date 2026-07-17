from app.domain.enums import (
    MetricType,
    ModelType,
    RegressionStatus,
)
from app.reports.models import (
    DatasetInformation,
    EvaluationReport,
    MetricReport,
    ModelInformation,
    RegressionMetricReport,
    RegressionReport,
    ReportMetadata,
    SummaryReport,
)


def test_evaluation_report_creation() -> None:
    metadata = ReportMetadata()

    model = ModelInformation(
        name="GPT",
        version="1.0",
        model_type=ModelType.LLM,
    )

    dataset = DatasetInformation(
        dataset_id="dataset-1",
        name="Medical QA",
        description="Demo dataset",
    )

    summary = SummaryReport(
        total_metrics=2,
        overall_score=0.95,
        evaluation_duration_ms=125.0,
        evaluation_status="completed",
    )

    metrics = [
        MetricReport(
            metric=MetricType.ACCURACY,
            value=0.95,
            higher_is_better=True,
        ),
        MetricReport(
            metric=MetricType.LATENCY,
            value=125.0,
            higher_is_better=False,
        ),
    ]

    report = EvaluationReport(
        metadata=metadata,
        model=model,
        dataset=dataset,
        summary=summary,
        metrics=metrics,
    )

    assert report.summary.total_metrics == 2
    assert len(report.metrics) == 2
    assert report.model.name == "GPT"


def test_regression_report_creation() -> None:
    metadata = ReportMetadata()

    comparison = RegressionMetricReport(
        metric=MetricType.ACCURACY,
        baseline_value=0.91,
        candidate_value=0.94,
        absolute_change=0.03,
        relative_change=0.033,
        status=RegressionStatus.PASSED,
    )

    report = RegressionReport(
        metadata=metadata,
        baseline_run_id="baseline",
        candidate_run_id="candidate",
        status=RegressionStatus.PASSED,
        comparisons=[comparison],
    )

    assert report.status == RegressionStatus.PASSED
    assert len(report.comparisons) == 1
