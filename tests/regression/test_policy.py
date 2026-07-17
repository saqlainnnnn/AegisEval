from app.domain.enums import (
    MetricType,
    RegressionStatus,
    ThresholdType,
)
from app.domain.regression import (
    RegressionThreshold,
)
from app.regression.policy import (
    RegressionThresholdPolicy,
)


def _absolute_threshold(
    value: float,
) -> RegressionThreshold:
    return RegressionThreshold(
        metric=MetricType.ACCURACY,
        threshold_type=(ThresholdType.ABSOLUTE),
        value=value,
    )


def _relative_threshold(
    value: float,
) -> RegressionThreshold:
    return RegressionThreshold(
        metric=MetricType.ACCURACY,
        threshold_type=(ThresholdType.RELATIVE),
        value=value,
    )


def test_higher_is_better_passes_within_absolute_threshold() -> None:
    policy = RegressionThresholdPolicy()

    status = policy.evaluate(
        baseline_value=0.90,
        candidate_value=0.87,
        higher_is_better=True,
        threshold=_absolute_threshold(0.05),
    )

    assert status == RegressionStatus.PASSED


def test_higher_is_better_detects_absolute_regression() -> None:
    policy = RegressionThresholdPolicy()

    status = policy.evaluate(
        baseline_value=0.90,
        candidate_value=0.80,
        higher_is_better=True,
        threshold=_absolute_threshold(0.05),
    )

    assert status == RegressionStatus.REGRESSION


def test_lower_is_better_passes_within_absolute_threshold() -> None:
    policy = RegressionThresholdPolicy()

    status = policy.evaluate(
        baseline_value=100.0,
        candidate_value=105.0,
        higher_is_better=False,
        threshold=_absolute_threshold(10.0),
    )

    assert status == RegressionStatus.PASSED


def test_lower_is_better_detects_absolute_regression() -> None:
    policy = RegressionThresholdPolicy()

    status = policy.evaluate(
        baseline_value=100.0,
        candidate_value=125.0,
        higher_is_better=False,
        threshold=_absolute_threshold(10.0),
    )

    assert status == RegressionStatus.REGRESSION


def test_higher_is_better_improvement_passes() -> None:
    policy = RegressionThresholdPolicy()

    status = policy.evaluate(
        baseline_value=0.80,
        candidate_value=0.95,
        higher_is_better=True,
        threshold=_absolute_threshold(0.01),
    )

    assert status == RegressionStatus.PASSED


def test_lower_is_better_improvement_passes() -> None:
    policy = RegressionThresholdPolicy()

    status = policy.evaluate(
        baseline_value=100.0,
        candidate_value=75.0,
        higher_is_better=False,
        threshold=_absolute_threshold(1.0),
    )

    assert status == RegressionStatus.PASSED


def test_exact_absolute_threshold_passes() -> None:
    policy = RegressionThresholdPolicy()

    status = policy.evaluate(
        baseline_value=0.90,
        candidate_value=0.85,
        higher_is_better=True,
        threshold=_absolute_threshold(0.05),
    )

    assert status == RegressionStatus.PASSED


def test_relative_threshold_passes_within_allowed_degradation() -> None:
    policy = RegressionThresholdPolicy()

    status = policy.evaluate(
        baseline_value=100.0,
        candidate_value=109.0,
        higher_is_better=False,
        threshold=_relative_threshold(0.10),
    )

    assert status == RegressionStatus.PASSED


def test_relative_threshold_detects_regression() -> None:
    policy = RegressionThresholdPolicy()

    status = policy.evaluate(
        baseline_value=100.0,
        candidate_value=111.0,
        higher_is_better=False,
        threshold=_relative_threshold(0.10),
    )

    assert status == RegressionStatus.REGRESSION


def test_relative_threshold_for_higher_is_better_metric() -> None:
    policy = RegressionThresholdPolicy()

    status = policy.evaluate(
        baseline_value=0.80,
        candidate_value=0.70,
        higher_is_better=True,
        threshold=_relative_threshold(0.10),
    )

    assert status == RegressionStatus.REGRESSION


def test_zero_baseline_with_relative_threshold() -> None:
    policy = RegressionThresholdPolicy()

    status = policy.evaluate(
        baseline_value=0.0,
        candidate_value=1.0,
        higher_is_better=False,
        threshold=_relative_threshold(0.10),
    )

    assert status == RegressionStatus.REGRESSION
