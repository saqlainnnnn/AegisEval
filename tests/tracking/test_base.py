import pytest

from app.tracking.base import BaseExperimentTracker, TrackingRun


def test_experiment_tracker_is_abstract() -> None:
    with pytest.raises(TypeError):
        BaseExperimentTracker()


def test_tracking_run_is_abstract() -> None:
    with pytest.raises(TypeError):
        TrackingRun()