from __future__ import annotations

from sqlalchemy.orm import Session

from app.database.models import DatasetRecord


class DatasetRepository:
    """
    Repository for persisted evaluation datasets.
    """

    def __init__(
        self,
        session: Session,
    ) -> None:
        self._session = session

    def add(
        self,
        dataset: DatasetRecord,
    ) -> None:
        self._session.add(dataset)

    def get(
        self,
        dataset_id: str,
    ) -> DatasetRecord | None:
        return self._session.get(
            DatasetRecord,
            dataset_id,
        )