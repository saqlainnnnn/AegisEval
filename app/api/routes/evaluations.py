from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.adapters.dummy import DummyAdapter
from app.api.dependencies import get_database_session
from app.api.models.evaluation import (
    CreateEvaluationRequest,
    CreateEvaluationResponse,
    EvaluationMetricResponse,
)
from app.benchmark.runner import BenchmarkRunner
from app.core.config import get_settings
from app.domain.dataset import (
    Dataset,
    DatasetMetadata,
    Question,
)
from app.domain.evaluation import ModelConfig
from app.metrics.accuracy import AccuracyMetric
from app.metrics.engine import MetricsEngine
from app.metrics.failure_rate import FailureRateMetric
from app.metrics.latency import LatencyMetric
from app.services.evaluation import EvaluationService
from app.services.persistence import (
    EvaluationPersistenceService,
)
from app.tracking.mlflow_tracker import MLflowTracker


router = APIRouter(
    prefix="/evaluations",
    tags=["evaluations"],
)


@router.post(
    "",
    response_model=CreateEvaluationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_evaluation(
    request: CreateEvaluationRequest,
    session: Session = Depends(
        get_database_session
    ),
) -> CreateEvaluationResponse:
    """
    Execute, track, and persist a new evaluation.
    """

    dataset = Dataset(
        metadata=DatasetMetadata(
            name=request.dataset.name,
            description=request.dataset.description,
            version=request.dataset.version,
        ),
        questions=[
            Question(
                question=question.question,
                expected_answer=(
                    question.expected_answer
                ),
            )
            for question in request.dataset.questions
        ],
    )

    model_config = ModelConfig(
        name=request.model.name,
        version=request.model.version,
        model_type=request.model.model_type,
        embedding_model=(
            request.model.embedding_model
        ),
        prompt_version=(
            request.model.prompt_version
        ),
        retriever=request.model.retriever,
        chunk_size=request.model.chunk_size,
        top_k=request.model.top_k,
    )

    adapter = DummyAdapter(
        model_config
    )

    runner = BenchmarkRunner(
        adapter
    )

    metrics_engine = MetricsEngine(
        [
            AccuracyMetric(),
            LatencyMetric(),
            FailureRateMetric(),
        ]
    )

    settings = get_settings()

    tracker = MLflowTracker(
        experiment_name=(
            settings.mlflow_experiment_name
        ),
        tracking_uri=(
            settings.mlflow_tracking_uri
        ),
    )

    evaluation_service = EvaluationService(
        runner=runner,
        metrics_engine=metrics_engine,
        tracker=tracker,
    )

    result = evaluation_service.evaluate(
        dataset
    )

    persistence_service = (
        EvaluationPersistenceService(
            session
        )
    )

    persistence_service.save(
        dataset=dataset,
        result=result,
    )

    metrics = [
        EvaluationMetricResponse(
            name=metric.metric.value,
            value=metric.value,
            higher_is_better=(
                metric.higher_is_better
            ),
        )
        for metric in result.metrics.metrics.values()
    ]

    return CreateEvaluationResponse(
        evaluation_id=result.evaluation.id,
        dataset_id=dataset.id,
        tracking_run_id=(
            result.tracking_run_id
        ),
        model_name=(
            result.evaluation.model.name
        ),
        model_version=(
            result.evaluation.model.version
        ),
        metrics=metrics,
    )