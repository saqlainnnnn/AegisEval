from __future__ import annotations

from collections.abc import Generator
from functools import lru_cache

from fastapi import Depends
from sqlalchemy import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings
from app.database.engine import create_database_engine
from app.database.session import create_session_factory
from app.metrics.accuracy import AccuracyMetric
from app.metrics.engine import MetricsEngine
from app.metrics.failure_rate import FailureRateMetric
from app.metrics.latency import LatencyMetric
from app.persistence.repositories import (
    EvaluationRunRepository,
)
from app.services.persistence import (
    EvaluationPersistenceService,
)
from app.tracking.mlflow_tracker import MLflowTracker

from app.persistence.repositories import (
    EvaluationRunRepository,
    RegressionRunRepository,
)
from app.regression.engine import RegressionEngine
from app.regression.policy import (
    RegressionThresholdPolicy,
)
from app.services.regression import RegressionService


@lru_cache
def get_database_engine() -> Engine:
    """
    Create and cache the application database engine.
    """

    settings = get_settings()

    return create_database_engine(
        settings.database_url
    )


@lru_cache
def get_session_factory() -> sessionmaker[Session]:
    """
    Create and cache the application session factory.
    """

    engine = get_database_engine()

    return create_session_factory(
        engine
    )


def get_database_session() -> Generator[
    Session,
    None,
    None,
]:
    """
    Provide a database session for one request.
    """

    session_factory = get_session_factory()

    with session_factory() as session:
        yield session


def get_metrics_engine() -> MetricsEngine:
    """
    Create the metrics engine used for evaluations.
    """

    return MetricsEngine(
        [
            AccuracyMetric(),
            LatencyMetric(),
            FailureRateMetric(),
        ]
    )


def get_experiment_tracker() -> MLflowTracker:
    """
    Create the configured experiment tracker.
    """

    settings = get_settings()

    return MLflowTracker(
        experiment_name=(
            settings.mlflow_experiment_name
        ),
        tracking_uri=(
            settings.mlflow_tracking_uri
        ),
    )


def get_persistence_service(
    session: Session = Depends(
        get_database_session
    ),
) -> EvaluationPersistenceService:
    """
    Create the evaluation persistence service.
    """

    return EvaluationPersistenceService(
        session
    )


def get_evaluation_run_repository(
    session: Session = Depends(
        get_database_session
    ),
) -> EvaluationRunRepository:
    """
    Create the evaluation run repository.
    """

    return EvaluationRunRepository(
        session
    )

def get_regression_run_repository(
    session: Session = Depends(
        get_database_session
    ),
) -> RegressionRunRepository:
    """
    Create the regression run repository.
    """

    return RegressionRunRepository(
        session
    )


def get_regression_engine() -> RegressionEngine:
    """
    Create the regression comparison engine.
    """

    return RegressionEngine(
        RegressionThresholdPolicy()
    )


def get_regression_service(
    evaluation_repository: EvaluationRunRepository = Depends(
        get_evaluation_run_repository
    ),
    regression_repository: RegressionRunRepository = Depends(
        get_regression_run_repository
    ),
    regression_engine: RegressionEngine = Depends(
        get_regression_engine
    ),
) -> RegressionService:
    """
    Create the regression orchestration service.
    """

    return RegressionService(
        evaluation_repository=(
            evaluation_repository
        ),
        regression_repository=(
            regression_repository
        ),
        regression_engine=(
            regression_engine
        ),
    )