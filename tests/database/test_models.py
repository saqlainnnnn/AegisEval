from datetime import UTC, datetime

from app.database.base import Base
from app.database.engine import create_database_engine
from app.database.models import (
    DatasetRecord,
    EvaluationRunRecord,
    MetricRecord,
    ModelRecord,
)
from app.database.session import create_session_factory


def test_create_database_schema() -> None:
    engine = create_database_engine("sqlite+pysqlite:///:memory:")

    Base.metadata.create_all(engine)

    table_names = set(Base.metadata.tables.keys())

    assert "models" in table_names
    assert "datasets" in table_names
    assert "evaluation_runs" in table_names
    assert "metrics" in table_names


def test_persist_complete_evaluation_relationships() -> None:
    engine = create_database_engine("sqlite+pysqlite:///:memory:")

    Base.metadata.create_all(engine)

    session_factory = create_session_factory(engine)

    now = datetime.now(UTC)

    model = ModelRecord(
        id="model-1",
        name="Dummy",
        version="1.0",
        model_type="custom",
        created_at=now,
    )

    dataset = DatasetRecord(
        id="dataset-1",
        name="Test Dataset",
        description="Database relationship test",
        version="1.0",
        created_at=now,
    )

    evaluation_run = EvaluationRunRecord(
        id="run-1",
        model=model,
        dataset=dataset,
        started_at=now,
        finished_at=now,
        duration_ms=10.0,
    )

    metric = MetricRecord(
        metric_type="accuracy",
        value=1.0,
        higher_is_better=True,
        metric_metadata={
            "correct": 1,
            "total": 1,
        },
    )

    evaluation_run.metrics.append(metric)

    with session_factory() as session:
        session.add(evaluation_run)
        session.commit()

        stored_run = session.get(
            EvaluationRunRecord,
            "run-1",
        )

        assert stored_run is not None
        assert stored_run.model.name == "Dummy"
        assert stored_run.dataset.name == "Test Dataset"

        assert len(stored_run.metrics) == 1
        assert stored_run.metrics[0].metric_type == "accuracy"
        assert stored_run.metrics[0].value == 1.0
