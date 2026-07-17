from app.domain.enums import ModelType
from app.reports.exporters.json_exporter import JsonReportExporter
from app.reports.models import (
    DatasetInformation,
    EvaluationReport,
    ModelInformation,
    ReportMetadata,
    SummaryReport,
)


def test_json_exporter() -> None:
    report = EvaluationReport(
        metadata=ReportMetadata(
            evaluation_run_id="run-1",
        ),
        model=ModelInformation(
            name="GPT",
            version="1.0",
            model_type=ModelType.LLM,
        ),
        dataset=DatasetInformation(
            dataset_id="dataset-1",
            name="Dataset",
            description="Demo",
        ),
        summary=SummaryReport(
            total_metrics=0,
            overall_score=None,
            evaluation_duration_ms=1.0,
            started_at=ReportMetadata(
                evaluation_run_id="x"
            ).generated_at,
            finished_at=ReportMetadata(
                evaluation_run_id="x"
            ).generated_at,
        ),
    )

    exporter = JsonReportExporter()

    output = exporter.export(report)

    assert '"model"' in output
    assert '"summary"' in output
    assert '"dataset"' in output