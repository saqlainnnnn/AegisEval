from __future__ import annotations

from collections.abc import Generator
from types import TracebackType

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.api.app import create_app
from app.api.dependencies import (
    get_database_session,
    get_experiment_tracker,
)
from app.database.base import Base
from app.database.engine import create_database_engine
from app.database.models import EvaluationRunRecord
from app.database.session import create_session_factory
from app.domain.evaluation import EvaluationResult
from app.domain.metrics import MetricSummary
from app.tracking.base import (
    BaseExperimentTracker,
    TrackingRun,
)


class FakeTrackingRun(TrackingRun):
    """
    In-memory tracking run used by API tests.
    """

    @property
    def run_id(self) -> str:
        return "fake-api-run-123"

    def __enter__(self) -> FakeTrackingRun:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        pass

    def log_metrics(
        self,
        summary: MetricSummary,
    ) -> None:
        pass

    def log_evaluation(self) -> None:
        pass


class FakeExperimentTracker(BaseExperimentTracker):
    """
    In-memory tracker used to isolate API tests from MLflow.
    """

    def start_run(
        self,
        evaluation: EvaluationResult,
    ) -> TrackingRun:
        return FakeTrackingRun()


def _create_test_client(
    tmp_path,
    database_name: str,
) -> tuple[
    TestClient,
    object,
]:
    """
    Create a test application backed by an isolated
    temporary SQLite database.
    """

    database_path = (
        tmp_path / database_name
    )

    engine = create_database_engine(
        "sqlite:///"
        f"{database_path.as_posix()}"
    )

    Base.metadata.create_all(
        engine
    )

    session_factory = create_session_factory(
        engine
    )

    def override_database_session(
    ) -> Generator[Session, None, None]:
        with session_factory() as session:
            yield session

    def override_experiment_tracker(
    ) -> BaseExperimentTracker:
        return FakeExperimentTracker()

    application = create_app()

    application.dependency_overrides[
        get_database_session
    ] = override_database_session

    application.dependency_overrides[
        get_experiment_tracker
    ] = override_experiment_tracker

    return (
        TestClient(application),
        session_factory,
    )


def _evaluation_payload(
    dataset_name: str,
) -> dict:
    """
    Build a valid evaluation request payload.
    """

    return {
        "model": {
            "name": "Dummy",
            "version": "1.0",
            "model_type": "custom",
            "prompt_version": "v1",
            "top_k": 5,
        },
        "dataset": {
            "name": dataset_name,
            "description": (
                "API integration test"
            ),
            "version": "1.0",
            "questions": [
                {
                    "question": "What is AI?",
                    "expected_answer": (
                        "Artificial Intelligence"
                    ),
                },
                {
                    "question": "What is ML?",
                    "expected_answer": (
                        "Machine Learning"
                    ),
                },
            ],
        },
    }


def test_create_evaluation(
    tmp_path,
) -> None:
    client, session_factory = (
        _create_test_client(
            tmp_path,
            "create_api_test.db",
        )
    )

    with client:
        response = client.post(
            "/api/v1/evaluations",
            json=_evaluation_payload(
                "API Evaluation Dataset"
            ),
        )

    assert response.status_code == 201

    data = response.json()

    assert data["model_name"] == "Dummy"
    assert data["model_version"] == "1.0"

    assert (
        data["tracking_run_id"]
        == "fake-api-run-123"
    )

    assert len(data["metrics"]) == 3

    metric_names = {
        metric["name"]
        for metric in data["metrics"]
    }

    assert "accuracy" in metric_names
    assert "latency" in metric_names
    assert "failure_rate" in metric_names

    with session_factory() as session:
        stored_run = session.get(
            EvaluationRunRecord,
            data["evaluation_id"],
        )

        assert stored_run is not None

        assert (
            stored_run.mlflow_run_id
            == "fake-api-run-123"
        )


def test_list_evaluations(
    tmp_path,
) -> None:
    client, _ = _create_test_client(
        tmp_path,
        "list_api_test.db",
    )

    with client:
        create_response = client.post(
            "/api/v1/evaluations",
            json=_evaluation_payload(
                "List Test Dataset"
            ),
        )

        assert (
            create_response.status_code
            == 201
        )

        response = client.get(
            "/api/v1/evaluations"
        )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1

    assert (
        data[0]["model_name"]
        == "Dummy"
    )

    assert (
        data[0]["dataset_name"]
        == "List Test Dataset"
    )

    assert (
        data[0]["tracking_run_id"]
        == "fake-api-run-123"
    )


def test_get_evaluation(
    tmp_path,
) -> None:
    client, _ = _create_test_client(
        tmp_path,
        "detail_api_test.db",
    )

    with client:
        create_response = client.post(
            "/api/v1/evaluations",
            json=_evaluation_payload(
                "Detail Test Dataset"
            ),
        )

        assert (
            create_response.status_code
            == 201
        )

        evaluation_id = (
            create_response.json()[
                "evaluation_id"
            ]
        )

        response = client.get(
            f"/api/v1/evaluations/"
            f"{evaluation_id}"
        )

    assert response.status_code == 200

    data = response.json()

    assert (
        data["evaluation_id"]
        == evaluation_id
    )

    assert data["model_name"] == "Dummy"

    assert (
        data["dataset_name"]
        == "Detail Test Dataset"
    )

    assert (
        data["tracking_run_id"]
        == "fake-api-run-123"
    )

    assert len(data["metrics"]) == 3

    metric_names = {
        metric["name"]
        for metric in data["metrics"]
    }

    assert "accuracy" in metric_names
    assert "latency" in metric_names
    assert "failure_rate" in metric_names


def test_get_unknown_evaluation_returns_404(
    tmp_path,
) -> None:
    client, _ = _create_test_client(
        tmp_path,
        "not_found_api_test.db",
    )

    with client:
        response = client.get(
            "/api/v1/evaluations/"
            "does-not-exist"
        )

    assert response.status_code == 404

    assert response.json() == {
        "detail": "Evaluation not found"
    }