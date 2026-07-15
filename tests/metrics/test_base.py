import pytest

from app.metrics.base import BaseMetric


def test_base_metric_is_abstract() -> None:
    with pytest.raises(TypeError):
        BaseMetric()