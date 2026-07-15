from collections.abc import Generator

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.api.app import create_app
from app.api.dependencies import (
    get_database_session,
)
from app.database.base import Base
from app.database.engine import (
    create_database_engine,
)
from app.database.models import (
    EvaluationRunRecord,
)
from app.database.session import (
    create_session_factory,
)


def test_create_evaluation(
    tmp_path,
) -> None:
    database_path = (
        tmp_path / "api_test.db"
    )

    engine = create_database_engine(
        "sqlite:///"
        f"{database_path.as_posix()}"
    )

    Base.metadata.create_all(
        engine
    )

    session_factory = (
        create_session_factory(
            engine
        )
    )

    def override_database_session(
    ) -> Generator[Session, None, None]:
        with session_factory() as session:
            yield session

    application = create_app()

    application.dependency_overrides[
        get_database_session
    ] = override_database_session

    with TestClient(application) as client:
        response = client.post(
            "/api/v1/evaluations",
            json={
                "model": {
                    "name": "Dummy",
                    "version": "1.0",
                    "model_type": "custom",
                    "prompt_version": "v1",
                    "top_k": 5,
                },
                "dataset": {
                    "name": "API Evaluation Dataset",
                    "description": (
                        "API integration test"
                    ),
                    "version": "1.0",
                    "questions": [
                        {
                            "question": (
                                "What is AI?"
                            ),
                            "expected_answer": (
                                "Artificial Intelligence"
                            ),
                        },
                        {
                            "question": (
                                "What is ML?"
                            ),
                            "expected_answer": (
                                "Machine Learning"
                            ),
                        },
                    ],
                },
            },
        )

    assert response.status_code == 201

    data = response.json()

    assert data["model_name"] == "Dummy"
    assert data["model_version"] == "1.0"

    assert data[
        "tracking_run_id"
    ] is not None

    assert len(
        data["metrics"]
    ) == 3

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
            == data["tracking_run_id"]
        )