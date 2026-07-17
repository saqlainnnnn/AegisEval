from __future__ import annotations

from uuid import uuid4

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
from app.reports.models import (
    DatasetInformation,
    EvaluationReport,
    MetricReport,
    ModelInformation,
    RegressionMetricReport as RegressionMetricReportModel,
    RegressionReport,
    ReportMetadata,
    SummaryReport,
)


class ReportBuilder:
    """
    Converts persisted SQLAlchemy records into immutable
    report models.
    """

    def build_evaluation_report(
        self,
        run: EvaluationRunRecord,
    ) -> EvaluationReport:
        return EvaluationReport(
            metadata=self._build_metadata(run),
            model=self._build_model_information(run.model),
            dataset=self._build_dataset_information(run.dataset),
            summary=self._build_summary(run),
            metrics=self._build_metric_reports(run.metrics),
        )

    def build_regression_report(
        self,
        run: RegressionRunRecord,
    ) -> RegressionReport:
        return RegressionReport(
            metadata=self._build_regression_metadata(run),
            baseline_run_id=run.baseline_run_id,
            candidate_run_id=run.candidate_run_id,
            status=RegressionStatus(run.status),
            comparisons=self._build_regression_metric_reports(
                run.comparisons
            ),
        )

    def _build_metadata(
        self,
        run: EvaluationRunRecord,
    ) -> ReportMetadata:
        return ReportMetadata(
            report_id=str(uuid4()),
            evaluation_run_id=run.id,
            mlflow_run_id=run.mlflow_run_id,
        )

    def _build_regression_metadata(
        self,
        run: RegressionRunRecord,
    ) -> ReportMetadata:
        return ReportMetadata(
            report_id=str(uuid4()),
            evaluation_run_id=run.id,
        )

    def _build_model_information(
        self,
        model: ModelRecord,
    ) -> ModelInformation:
        return ModelInformation(
            name=model.name,
            version=model.version,
            model_type=ModelType(model.model_type),
            embedding_model=model.embedding_model,
            prompt_version=model.prompt_version,
            retriever=model.retriever,
            chunk_size=model.chunk_size,
            top_k=model.top_k,
        )

    def _build_dataset_information(
        self,
        dataset: DatasetRecord,
    ) -> DatasetInformation:
        return DatasetInformation(
            dataset_id=dataset.id,
            name=dataset.name,
            description=dataset.description,
            version=dataset.version,
        )

    def _build_summary(
        self,
        run: EvaluationRunRecord,
    ) -> SummaryReport:
        return SummaryReport(
            total_metrics=len(run.metrics),
            overall_score=None,
            evaluation_duration_ms=run.duration_ms,
            started_at=run.started_at,
            finished_at=run.finished_at,
        )

    def _build_metric_reports(
        self,
        metrics: list[MetricRecord],
    ) -> list[MetricReport]:
        reports: list[MetricReport] = []

        for metric in metrics:
            reports.append(
                MetricReport(
                    metric=MetricType(metric.metric_type),
                    value=metric.value,
                    higher_is_better=metric.higher_is_better,
                    metadata=metric.metric_metadata,
                )
            )

        return reports

    def _build_regression_metric_reports(
        self,
        metrics: list[RegressionMetricRecord],
    ) -> list[RegressionMetricReportModel]:
        reports: list[
            RegressionMetricReportModel
        ] = []

        for metric in metrics:
            reports.append(
                RegressionMetricReportModel(
                    metric=MetricType(metric.metric_type),
                    baseline_value=metric.baseline_value,
                    candidate_value=metric.candidate_value,
                    absolute_change=metric.absolute_change,
                    relative_change=metric.relative_change,
                    status=RegressionStatus(metric.status),
                )
            )

        return reports