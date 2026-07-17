from app.domain.enums import (
    ModelType,
    RegressionStatus,
)
from app.reports.exporters.markdown_exporter import (
    MarkdownReportExporter,
)
from app.reports.models import (
    DatasetInformation,
    EvaluationReport,
    ModelInformation,
    RegressionReport,
    ReportMetadata,
    SummaryReport,
)


def test_markdown_evaluation() -> None:
    metadata = ReportMetadata(
        evaluation_run_id="run-1",
    )

    report = EvaluationReport(
        metadata=metadata,
        model=ModelInformation(
            name="GPT",
            version="1.0",
            model_type=ModelType.LLM,
        ),
        dataset=DatasetInformation(
            dataset_id="dataset",
            name="Medical QA",
            description="Demo",
        ),
        summary=SummaryReport(
            total_metrics=0,
            overall_score=None,
            evaluation_duration_ms=100,
            started_at=metadata.generated_at,
            finished_at=metadata.generated_at,
        ),
    )

    exporter = MarkdownReportExporter()

    output = exporter.export_evaluation(report)

    assert "# Evaluation Report" in output
    assert "Medical QA" in output
    assert "GPT" in output


def test_markdown_regression() -> None:
    report = RegressionReport(
        metadata=ReportMetadata(
            evaluation_run_id="regression-1",
        ),
        baseline_run_id="baseline",
        candidate_run_id="candidate",
        status=RegressionStatus.PASSED,
    )

    exporter = MarkdownReportExporter()

    output = exporter.export_regression(report)

    assert "# Regression Report" in output
    assert "baseline" in output
    assert "candidate" in output