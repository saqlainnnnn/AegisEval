from __future__ import annotations

from app.reports.models import (
    EvaluationReport,
    RegressionReport,
)


class MarkdownReportExporter:
    """
    Exports reports in Markdown format.
    """

    def export_evaluation(
        self,
        report: EvaluationReport,
    ) -> str:
        lines: list[str] = [
            "# Evaluation Report",
            "",
            "## Metadata",
            f"- Report ID: {report.metadata.report_id}",
            f"- Evaluation Run: {report.metadata.evaluation_run_id}",
            f"- Generated At: {report.metadata.generated_at.isoformat()}",
            "",
            "## Model",
            f"- Name: {report.model.name}",
            f"- Version: {report.model.version}",
            f"- Type: {report.model.model_type.value}",
            "",
            "## Dataset",
            f"- Name: {report.dataset.name}",
            f"- Version: {report.dataset.version}",
            "",
            "## Summary",
            f"- Metrics: {report.summary.total_metrics}",
            f"- Duration: {report.summary.evaluation_duration_ms:.2f} ms",
            "",
            "## Metrics",
        ]

        for metric in report.metrics:
            lines.append(
                f"- {metric.metric.value}: {metric.value}"
            )

        return "\n".join(lines)

    def export_regression(
        self,
        report: RegressionReport,
    ) -> str:
        lines: list[str] = [
            "# Regression Report",
            "",
            f"Status: **{report.status.value}**",
            "",
            f"Baseline Run: {report.baseline_run_id}",
            f"Candidate Run: {report.candidate_run_id}",
            "",
            "## Metric Comparison",
        ]

        for comparison in report.comparisons:
            lines.append(
                (
                    f"- {comparison.metric.value}: "
                    f"{comparison.baseline_value} → "
                    f"{comparison.candidate_value} "
                    f"({comparison.status.value})"
                )
            )

        return "\n".join(lines)