from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import (
    Session,
    selectinload,
)

from app.database.models import EvaluationRunRecord


class EvaluationRunRepository:
    """
    Repository for persisted evaluation runs.
    """

    def __init__(
        self,
        session: Session,
    ) -> None:
        self._session = session

    def add(
        self,
        evaluation_run: EvaluationRunRecord,
    ) -> None:
        self._session.add(evaluation_run)

    def get(
        self,
        run_id: str,
    ) -> EvaluationRunRecord | None:
        statement = (
            select(EvaluationRunRecord)
            .options(
                selectinload(EvaluationRunRecord.model),
                selectinload(EvaluationRunRecord.dataset),
                selectinload(EvaluationRunRecord.metrics),
            )
            .where(EvaluationRunRecord.id == run_id)
        )

        return self._session.scalar(statement)

    def list_all(
        self,
    ) -> list[EvaluationRunRecord]:
        statement = (
            select(EvaluationRunRecord)
            .options(
                selectinload(EvaluationRunRecord.model),
                selectinload(EvaluationRunRecord.dataset),
                selectinload(EvaluationRunRecord.metrics),
            )
            .order_by(
                EvaluationRunRecord.started_at.desc()
            )
        )

        return list(
            self._session.scalars(statement).all()
        )