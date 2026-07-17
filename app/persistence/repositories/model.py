from __future__ import annotations

from sqlalchemy.orm import Session

from app.database.models import ModelRecord


class ModelRepository:
    """
    Repository for persisted model configurations.
    """

    def __init__(
        self,
        session: Session,
    ) -> None:
        self._session = session

    def add(
        self,
        model: ModelRecord,
    ) -> None:
        self._session.add(model)

    def get(
        self,
        model_id: str,
    ) -> ModelRecord | None:
        return self._session.get(
            ModelRecord,
            model_id,
        )
