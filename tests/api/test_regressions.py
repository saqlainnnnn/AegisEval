from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from app.api.dependencies import (
    get_database_session,
)
from app.database.base import Base
from app.database.engine import (
    create_database_engine,
)
from app.database.session import (
    create_session_factory,
)
from app.main import app


def _create_test_client(
    tmp_path: Path,
    database_name: str,
) -> TestClient:
    """
    Create an isolated API client backed by a
    temporary SQLite database.
    """

    database_path = tmp_path / database_name

    database_url = "sqlite+pysqlite:///" f"{database_path.as_posix()}"

    engine = create_database_engine(database_url)

    Base.metadata.create_all(engine)

    session_factory = create_session_factory(engine)

    def override_database_session():
        with session_factory() as session:
            yield session

    app.dependency_overrides[get_database_session] = override_database_session

    return TestClient(app)


def _evaluation_payload(
    dataset_name: str,
) -> dict:
    """
    Build a valid evaluation request.
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
            "description": ("Regression API test dataset"),
            "version": "1.0",
            "questions": [
                {
                    "question": "What is AI?",
                    "expected_answer": ("Artificial Intelligence"),
                }
            ],
        },
    }


def _create_evaluation(
    client: TestClient,
    dataset_name: str,
) -> str:
    """
    Create an evaluation and return its ID.
    """

    response = client.post(
        "/api/v1/evaluations",
        json=_evaluation_payload(dataset_name),
    )

    assert response.status_code == 201

    return response.json()["evaluation_id"]


def _regression_payload(
    *,
    baseline_run_id: str,
    candidate_run_id: str,
) -> dict:
    """
    Build a valid regression request.
    """

    return {
        "baseline_run_id": (baseline_run_id),
        "candidate_run_id": (candidate_run_id),
        "thresholds": [
            {
                "metric": "accuracy",
                "threshold_type": ("absolute"),
                "value": 0.05,
            },
            {
                "metric": "latency",
                "threshold_type": ("absolute"),
                "value": 1000.0,
            },
        ],
    }


def test_create_regression(
    tmp_path: Path,
) -> None:
    client = _create_test_client(
        tmp_path,
        "create_regression_api.db",
    )

    try:
        with client:
            baseline_run_id = _create_evaluation(
                client,
                "Baseline Dataset",
            )

            candidate_run_id = _create_evaluation(
                client,
                "Candidate Dataset",
            )

            response = client.post(
                "/api/v1/regressions",
                json=_regression_payload(
                    baseline_run_id=(baseline_run_id),
                    candidate_run_id=(candidate_run_id),
                ),
            )

        assert response.status_code == 201

        body = response.json()

        assert body["regression_id"]

        assert body["baseline_run_id"] == baseline_run_id

        assert body["candidate_run_id"] == candidate_run_id

        assert body["status"] == "passed"

        assert len(body["comparisons"]) == 2

        metric_names = {comparison["metric"] for comparison in body["comparisons"]}

        assert "accuracy" in metric_names
        assert "latency" in metric_names

    finally:
        app.dependency_overrides.clear()


def test_get_regression(
    tmp_path: Path,
) -> None:
    client = _create_test_client(
        tmp_path,
        "get_regression_api.db",
    )

    try:
        with client:
            baseline_run_id = _create_evaluation(
                client,
                "Baseline Dataset",
            )

            candidate_run_id = _create_evaluation(
                client,
                "Candidate Dataset",
            )

            create_response = client.post(
                "/api/v1/regressions",
                json=_regression_payload(
                    baseline_run_id=(baseline_run_id),
                    candidate_run_id=(candidate_run_id),
                ),
            )

            assert create_response.status_code == 201

            regression_id = create_response.json()["regression_id"]

            response = client.get("/api/v1/regressions/" f"{regression_id}")

        assert response.status_code == 200

        body = response.json()

        assert body["regression_id"] == regression_id

        assert body["baseline_run_id"] == baseline_run_id

        assert body["candidate_run_id"] == candidate_run_id

        assert len(body["comparisons"]) == 2

    finally:
        app.dependency_overrides.clear()


def test_get_unknown_regression_returns_404(
    tmp_path: Path,
) -> None:
    client = _create_test_client(
        tmp_path,
        "unknown_regression_api.db",
    )

    try:
        with client:
            response = client.get("/api/v1/regressions/" "missing-regression")

        assert response.status_code == 404

        assert response.json() == {"detail": ("Regression not found")}

    finally:
        app.dependency_overrides.clear()


def test_create_regression_rejects_missing_baseline(
    tmp_path: Path,
) -> None:
    client = _create_test_client(
        tmp_path,
        "missing_baseline_api.db",
    )

    try:
        with client:
            candidate_run_id = _create_evaluation(
                client,
                "Candidate Dataset",
            )

            response = client.post(
                "/api/v1/regressions",
                json=_regression_payload(
                    baseline_run_id=("missing-baseline"),
                    candidate_run_id=(candidate_run_id),
                ),
            )

        assert response.status_code == 404

        assert "Baseline evaluation run" in response.json()["detail"]

    finally:
        app.dependency_overrides.clear()


def test_create_regression_rejects_missing_candidate(
    tmp_path: Path,
) -> None:
    client = _create_test_client(
        tmp_path,
        "missing_candidate_api.db",
    )

    try:
        with client:
            baseline_run_id = _create_evaluation(
                client,
                "Baseline Dataset",
            )

            response = client.post(
                "/api/v1/regressions",
                json=_regression_payload(
                    baseline_run_id=(baseline_run_id),
                    candidate_run_id=("missing-candidate"),
                ),
            )

        assert response.status_code == 404

        assert "Candidate evaluation run" in response.json()["detail"]

    finally:
        app.dependency_overrides.clear()


def test_create_regression_requires_thresholds(
    tmp_path: Path,
) -> None:
    client = _create_test_client(
        tmp_path,
        "threshold_validation_api.db",
    )

    try:
        with client:
            response = client.post(
                "/api/v1/regressions",
                json={
                    "baseline_run_id": ("baseline-run"),
                    "candidate_run_id": ("candidate-run"),
                    "thresholds": [],
                },
            )

        assert response.status_code == 422

    finally:
        app.dependency_overrides.clear()
