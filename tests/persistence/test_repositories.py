from datetime import UTC, datetime

from app.database.base import Base
from app.database.engine import create_database_engine
from app.database.models import (
    DatasetRecord,
    EvaluationRunRecord,
    ModelRecord,
)
from app.database.session import create_session_factory
from app.persistence.repositories import (
    DatasetRepository,
    EvaluationRunRepository,
    ModelRepository,
)


def _create_session():
    engine = create_database_engine("sqlite+pysqlite:///:memory:")

    Base.metadata.create_all(engine)

    session_factory = create_session_factory(engine)

    return session_factory()


def test_model_repository_add_and_get() -> None:
    session = _create_session()

    try:
        repository = ModelRepository(session)

        model = ModelRecord(
            id="model-1",
            name="Dummy",
            version="1.0",
            model_type="custom",
            created_at=datetime.now(UTC),
        )

        repository.add(model)
        session.commit()

        stored = repository.get("model-1")

        assert stored is not None
        assert stored.name == "Dummy"
        assert stored.version == "1.0"

    finally:
        session.close()


def test_dataset_repository_add_and_get() -> None:
    session = _create_session()

    try:
        repository = DatasetRepository(session)

        dataset = DatasetRecord(
            id="dataset-1",
            name="Test Dataset",
            description="Repository test",
            version="1.0",
            created_at=datetime.now(UTC),
        )

        repository.add(dataset)
        session.commit()

        stored = repository.get("dataset-1")

        assert stored is not None
        assert stored.name == "Test Dataset"

    finally:
        session.close()


def test_evaluation_run_repository() -> None:
    session = _create_session()

    try:
        model_repository = ModelRepository(session)

        dataset_repository = DatasetRepository(session)

        run_repository = EvaluationRunRepository(session)

        now = datetime.now(UTC)

        model_repository.add(
            ModelRecord(
                id="model-1",
                name="Dummy",
                version="1.0",
                model_type="custom",
                created_at=now,
            )
        )

        dataset_repository.add(
            DatasetRecord(
                id="dataset-1",
                name="Test Dataset",
                description="Repository test",
                version="1.0",
                created_at=now,
            )
        )

        evaluation_run = EvaluationRunRecord(
            id="run-1",
            model_id="model-1",
            dataset_id="dataset-1",
            started_at=now,
            finished_at=now,
            duration_ms=10.0,
        )

        run_repository.add(evaluation_run)

        session.commit()

        stored = run_repository.get("run-1")

        assert stored is not None
        assert stored.model_id == "model-1"
        assert stored.dataset_id == "dataset-1"

        runs = run_repository.list_all()

        assert len(runs) == 1
        assert runs[0].id == "run-1"

    finally:
        session.close()
