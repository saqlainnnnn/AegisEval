from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.database.models import (
    DatasetRecord,
    EvaluationRunRecord,
    MetricRecord,
    ModelRecord,
)
from app.domain.dataset import Dataset
from app.domain.evaluation import ModelConfig
from app.persistence.repositories import (
    DatasetRepository,
    EvaluationRunRepository,
    ModelRepository,
)
from app.services.evaluation import EvaluationServiceResult


class EvaluationPersistenceService:
    """
    Persists completed evaluation results.

    A model, dataset, evaluation run, and its metrics are
    persisted within a single database transaction.
    """

    def __init__(
        self,
        session: Session,
    ) -> None:
        self._session = session

        self._model_repository = ModelRepository(session)

        self._dataset_repository = DatasetRepository(session)

        self._run_repository = EvaluationRunRepository(session)

    def save(
        self,
        dataset: Dataset,
        result: EvaluationServiceResult,
    ) -> EvaluationRunRecord:
        """
        Persist a completed evaluation workflow.
        """

        try:
            model_record = self._get_or_create_model(result.evaluation.model)

            dataset_record = self._get_or_create_dataset(dataset)

            evaluation_run = self._build_run_record(
                result=result,
                model_record=model_record,
                dataset_record=dataset_record,
            )

            self._run_repository.add(evaluation_run)

            self._session.commit()

            return evaluation_run

        except Exception:
            self._session.rollback()
            raise

    def _get_or_create_model(
        self,
        model: ModelConfig,
    ) -> ModelRecord:
        model_id = self._build_model_id(model)

        existing = self._model_repository.get(model_id)

        if existing is not None:
            return existing

        record = ModelRecord(
            id=model_id,
            name=model.name,
            version=model.version,
            model_type=model.model_type.value,
            embedding_model=model.embedding_model,
            prompt_version=model.prompt_version,
            retriever=model.retriever,
            chunk_size=model.chunk_size,
            top_k=model.top_k,
            created_at=datetime.now(UTC),
        )

        self._model_repository.add(record)

        return record

    def _get_or_create_dataset(
        self,
        dataset: Dataset,
    ) -> DatasetRecord:
        dataset_id = str(dataset.id)

        existing = self._dataset_repository.get(dataset_id)

        if existing is not None:
            return existing

        record = DatasetRecord(
            id=dataset_id,
            name=dataset.metadata.name,
            description=dataset.metadata.description,
            version=dataset.metadata.version,
            created_at=datetime.now(UTC),
        )

        self._dataset_repository.add(record)

        return record

    def _build_run_record(
        self,
        result: EvaluationServiceResult,
        model_record: ModelRecord,
        dataset_record: DatasetRecord,
    ) -> EvaluationRunRecord:
        evaluation = result.evaluation

        run = EvaluationRunRecord(
            id=str(evaluation.id),
            model=model_record,
            dataset=dataset_record,
            mlflow_run_id=result.tracking_run_id,
            started_at=evaluation.started_at,
            finished_at=evaluation.finished_at,
            duration_ms=evaluation.duration_ms,
        )

        for metric_result in result.metrics.metrics.values():
            run.metrics.append(
                MetricRecord(
                    metric_type=metric_result.metric.value,
                    value=metric_result.value,
                    higher_is_better=(metric_result.higher_is_better),
                    metric_metadata=(metric_result.metadata),
                )
            )

        return run

    @staticmethod
    def _build_model_id(
        model: ModelConfig,
    ) -> str:
        """
        Build a deterministic identifier from the model
        configuration.
        """

        serialized = json.dumps(
            model.model_dump(mode="json"),
            sort_keys=True,
            separators=(",", ":"),
        )

        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()[:36]
