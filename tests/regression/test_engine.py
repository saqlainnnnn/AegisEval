import pytest

from app.domain.enums import (
    MetricType,
    RegressionStatus,
    ThresholdType,
)
from app.domain.metrics import (
    MetricResult,
    MetricSummary,
)
from app.domain.regression import (
    RegressionThreshold,
)
from app.regression.engine import (
    RegressionEngine,
)
from app.regression.policy import (
    RegressionThresholdPolicy,
)


def _build_summary(
    *,
    accuracy: float | None = None,
    latency: float | None = None,
) -> MetricSummary:
    metrics = {}

    if accuracy is not None:
        metrics[MetricType.ACCURACY] = MetricResult(
            metric=MetricType.ACCURACY,
            value=accuracy,
            higher_is_better=True,
        )

    if latency is not None:
        metrics[MetricType.LATENCY] = MetricResult(
            metric=MetricType.LATENCY,
            value=latency,
            higher_is_better=False,
        )

    return MetricSummary(metrics=metrics)


def _build_engine() -> RegressionEngine:
    return RegressionEngine(RegressionThresholdPolicy())


def test_compare_passes_when_metrics_are_within_thresholds() -> None:
    engine = _build_engine()

    result = engine.compare(
        baseline_run_id="baseline-run",
        candidate_run_id="candidate-run",
        baseline=_build_summary(
            accuracy=0.90,
            latency=100.0,
        ),
        candidate=_build_summary(
            accuracy=0.88,
            latency=105.0,
        ),
        thresholds=[
            RegressionThreshold(
                metric=MetricType.ACCURACY,
                threshold_type=(ThresholdType.ABSOLUTE),
                value=0.05,
            ),
            RegressionThreshold(
                metric=MetricType.LATENCY,
                threshold_type=(ThresholdType.RELATIVE),
                value=0.10,
            ),
        ],
    )

    assert result.status == RegressionStatus.PASSED

    assert len(result.comparisons) == 2


def test_compare_detects_regression() -> None:
    engine = _build_engine()

    result = engine.compare(
        baseline_run_id="baseline-run",
        candidate_run_id="candidate-run",
        baseline=_build_summary(
            accuracy=0.90,
            latency=100.0,
        ),
        candidate=_build_summary(
            accuracy=0.70,
            latency=105.0,
        ),
        thresholds=[
            RegressionThreshold(
                metric=MetricType.ACCURACY,
                threshold_type=(ThresholdType.ABSOLUTE),
                value=0.05,
            ),
            RegressionThreshold(
                metric=MetricType.LATENCY,
                threshold_type=(ThresholdType.ABSOLUTE),
                value=10.0,
            ),
        ],
    )

    assert result.status == RegressionStatus.REGRESSION

    accuracy_comparison = result.comparisons[0]

    assert accuracy_comparison.status == RegressionStatus.REGRESSION

    assert accuracy_comparison.absolute_change == pytest.approx(-0.20)


def test_compare_calculates_relative_change() -> None:
    engine = _build_engine()

    result = engine.compare(
        baseline_run_id="baseline-run",
        candidate_run_id="candidate-run",
        baseline=_build_summary(latency=100.0),
        candidate=_build_summary(latency=120.0),
        thresholds=[
            RegressionThreshold(
                metric=MetricType.LATENCY,
                threshold_type=(ThresholdType.RELATIVE),
                value=0.25,
            )
        ],
    )

    comparison = result.comparisons[0]

    assert comparison.absolute_change == pytest.approx(20.0)

    assert comparison.relative_change == pytest.approx(0.20)


def test_compare_uses_none_relative_change_for_zero_baseline() -> None:
    engine = _build_engine()

    result = engine.compare(
        baseline_run_id="baseline-run",
        candidate_run_id="candidate-run",
        baseline=_build_summary(latency=0.0),
        candidate=_build_summary(latency=1.0),
        thresholds=[
            RegressionThreshold(
                metric=MetricType.LATENCY,
                threshold_type=(ThresholdType.ABSOLUTE),
                value=2.0,
            )
        ],
    )

    assert result.comparisons[0].relative_change is None


def test_compare_rejects_missing_baseline_metric() -> None:
    engine = _build_engine()

    with pytest.raises(
        ValueError,
        match=("Metric accuracy is missing " "from baseline summary"),
    ):
        engine.compare(
            baseline_run_id="baseline-run",
            candidate_run_id="candidate-run",
            baseline=_build_summary(latency=100.0),
            candidate=_build_summary(accuracy=0.90),
            thresholds=[
                RegressionThreshold(
                    metric=(MetricType.ACCURACY),
                    threshold_type=(ThresholdType.ABSOLUTE),
                    value=0.05,
                )
            ],
        )


def test_compare_rejects_missing_candidate_metric() -> None:
    engine = _build_engine()

    with pytest.raises(
        ValueError,
        match=("Metric accuracy is missing " "from candidate summary"),
    ):
        engine.compare(
            baseline_run_id="baseline-run",
            candidate_run_id="candidate-run",
            baseline=_build_summary(accuracy=0.90),
            candidate=_build_summary(latency=100.0),
            thresholds=[
                RegressionThreshold(
                    metric=(MetricType.ACCURACY),
                    threshold_type=(ThresholdType.ABSOLUTE),
                    value=0.05,
                )
            ],
        )
