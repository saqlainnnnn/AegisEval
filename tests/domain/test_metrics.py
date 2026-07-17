from app.domain.enums import MetricType
from app.domain.metrics import MetricResult, MetricSummary


def test_metric_result_creation() -> None:
    metric = MetricResult(
        metric=MetricType.ACCURACY,
        value=0.95,
    )

    assert metric.metric == MetricType.ACCURACY
    assert metric.value == 0.95
    assert metric.higher_is_better is True


def test_metric_summary_defaults() -> None:
    summary = MetricSummary()

    assert summary.metrics == {}
    assert summary.overall_score is None


def test_metric_summary_store_metric() -> None:
    accuracy = MetricResult(
        metric=MetricType.ACCURACY,
        value=0.95,
    )

    summary = MetricSummary(
        metrics={
            MetricType.ACCURACY: accuracy,
        }
    )

    assert summary.metrics[MetricType.ACCURACY].value == 0.95
