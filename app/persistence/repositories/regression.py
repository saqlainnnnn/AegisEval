from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.database.models.regression import (
    RegressionMetricRecord,
    RegressionRunRecord,
)
from app.domain.regression import RegressionResult


class RegressionRunRepository:
    """
    Persistence operations for regression results.
    """

    def __init__(
        self,
        session: Session,
    ) -> None:
        self._session = session

    def save(
        self,
        result: RegressionResult,
    ) -> RegressionRunRecord:
        """
        Persist a complete regression result.
        """

        record = RegressionRunRecord(
            baseline_run_id=(result.baseline_run_id),
            candidate_run_id=(result.candidate_run_id),
            status=result.status.value,
            comparisons=[
                RegressionMetricRecord(
                    metric_type=(comparison.metric.value),
                    baseline_value=(comparison.baseline_value),
                    candidate_value=(comparison.candidate_value),
                    absolute_change=(comparison.absolute_change),
                    relative_change=(comparison.relative_change),
                    threshold_type=(comparison.threshold.threshold_type.value),
                    threshold_value=(comparison.threshold.value),
                    status=(comparison.status.value),
                )
                for comparison in result.comparisons
            ],
        )

        self._session.add(record)
        self._session.commit()
        self._session.refresh(record)

        return record

    def get(
        self,
        regression_id: str,
    ) -> RegressionRunRecord | None:
        """
        Return one regression result.
        """

        statement = (
            select(RegressionRunRecord)
            .options(selectinload(RegressionRunRecord.comparisons))
            .where(RegressionRunRecord.id == regression_id)
        )

        return self._session.scalar(statement)

    def list_all(
        self,
    ) -> list[RegressionRunRecord]:
        """
        Return all persisted regression results.
        """

        statement = select(RegressionRunRecord).options(
            selectinload(RegressionRunRecord.comparisons)
        )

        return list(self._session.scalars(statement).all())
