import pytest
from pydantic import ValidationError

from app.domain.enums import (
    MetricType,
    RegressionStatus,
    ThresholdType,
)
from app.domain.regression import (
    MetricComparison,
    RegressionResult,
    RegressionThreshold,
)


def _build_threshold() -> RegressionThreshold:
    return RegressionThreshold(
        metric=MetricType.ACCURACY,
        threshold_type=(ThresholdType.ABSOLUTE),
        value=0.05,
    )


def test_regression_threshold() -> None:
    threshold = _build_threshold()

    assert threshold.metric == MetricType.ACCURACY

    assert threshold.threshold_type == ThresholdType.ABSOLUTE

    assert threshold.value == 0.05


def test_regression_threshold_rejects_negative_value() -> None:
    with pytest.raises(ValidationError):
        RegressionThreshold(
            metric=MetricType.ACCURACY,
            threshold_type=(ThresholdType.ABSOLUTE),
            value=-0.01,
        )


def test_metric_comparison() -> None:
    comparison = MetricComparison(
        metric=MetricType.ACCURACY,
        baseline_value=0.90,
        candidate_value=0.85,
        absolute_change=-0.05,
        relative_change=(-0.05 / 0.90),
        threshold=_build_threshold(),
        status=(RegressionStatus.PASSED),
    )

    assert comparison.metric == MetricType.ACCURACY

    assert comparison.absolute_change == pytest.approx(-0.05)


def test_regression_result_passed() -> None:
    comparison = MetricComparison(
        metric=MetricType.ACCURACY,
        baseline_value=0.90,
        candidate_value=0.88,
        absolute_change=-0.02,
        relative_change=(-0.02 / 0.90),
        threshold=_build_threshold(),
        status=(RegressionStatus.PASSED),
    )

    result = RegressionResult(
        baseline_run_id="baseline-run",
        candidate_run_id="candidate-run",
        status=RegressionStatus.PASSED,
        comparisons=[comparison],
    )

    assert result.status == RegressionStatus.PASSED


def test_regression_result_with_regression() -> None:
    comparison = MetricComparison(
        metric=MetricType.ACCURACY,
        baseline_value=0.90,
        candidate_value=0.70,
        absolute_change=-0.20,
        relative_change=(-0.20 / 0.90),
        threshold=_build_threshold(),
        status=(RegressionStatus.REGRESSION),
    )

    result = RegressionResult(
        baseline_run_id="baseline-run",
        candidate_run_id="candidate-run",
        status=(RegressionStatus.REGRESSION),
        comparisons=[comparison],
    )

    assert result.status == RegressionStatus.REGRESSION


def test_regression_result_rejects_inconsistent_status() -> None:
    comparison = MetricComparison(
        metric=MetricType.ACCURACY,
        baseline_value=0.90,
        candidate_value=0.70,
        absolute_change=-0.20,
        relative_change=(-0.20 / 0.90),
        threshold=_build_threshold(),
        status=(RegressionStatus.REGRESSION),
    )

    with pytest.raises(ValidationError):
        RegressionResult(
            baseline_run_id="baseline-run",
            candidate_run_id="candidate-run",
            status=RegressionStatus.PASSED,
            comparisons=[comparison],
        )


def test_regression_result_requires_comparisons() -> None:
    with pytest.raises(ValidationError):
        RegressionResult(
            baseline_run_id="baseline-run",
            candidate_run_id="candidate-run",
            status=RegressionStatus.PASSED,
            comparisons=[],
        )
