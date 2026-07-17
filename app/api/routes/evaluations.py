from __future__ import annotations

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from app.adapters.dummy import DummyAdapter
from app.api.dependencies import (
    get_evaluation_run_repository,
    get_experiment_tracker,
    get_metrics_engine,
    get_persistence_service,
)
from app.api.models.evaluation import (
    CreateEvaluationRequest,
    CreateEvaluationResponse,
    EvaluationDetailResponse,
    EvaluationListItemResponse,
    EvaluationMetricResponse,
)
from app.benchmark.runner import BenchmarkRunner
from app.domain.dataset import (
    Dataset,
    DatasetMetadata,
    Question,
)
from app.domain.evaluation import ModelConfig
from app.metrics.engine import MetricsEngine
from app.persistence.repositories import (
    EvaluationRunRepository,
)
from app.services.evaluation import EvaluationService
from app.services.persistence import (
    EvaluationPersistenceService,
)
from app.tracking.base import BaseExperimentTracker

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
    metrics_engine: MetricsEngine = Depends(get_metrics_engine),
    tracker: BaseExperimentTracker = Depends(get_experiment_tracker),
    persistence_service: EvaluationPersistenceService = Depends(
        get_persistence_service
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
                expected_answer=(question.expected_answer),
            )
            for question in request.dataset.questions
        ],
    )

    model_config = ModelConfig(
        name=request.model.name,
        version=request.model.version,
        model_type=request.model.model_type,
        embedding_model=(request.model.embedding_model),
        prompt_version=(request.model.prompt_version),
        retriever=request.model.retriever,
        chunk_size=request.model.chunk_size,
        top_k=request.model.top_k,
    )

    adapter = DummyAdapter(model_config)

    runner = BenchmarkRunner(adapter)

    evaluation_service = EvaluationService(
        runner=runner,
        metrics_engine=metrics_engine,
        tracker=tracker,
    )

    result = evaluation_service.evaluate(dataset)

    persistence_service.save(
        dataset=dataset,
        result=result,
    )

    metrics = [
        EvaluationMetricResponse(
            name=metric.metric.value,
            value=metric.value,
            higher_is_better=(metric.higher_is_better),
        )
        for metric in result.metrics.metrics.values()
    ]

    return CreateEvaluationResponse(
        evaluation_id=result.evaluation.id,
        dataset_id=dataset.id,
        tracking_run_id=result.tracking_run_id,
        model_name=result.evaluation.model.name,
        model_version=(result.evaluation.model.version),
        metrics=metrics,
    )


@router.get(
    "",
    response_model=list[EvaluationListItemResponse],
)
def list_evaluations(
    repository: EvaluationRunRepository = Depends(get_evaluation_run_repository),
) -> list[EvaluationListItemResponse]:
    """
    Return all persisted evaluation runs.
    """

    runs = repository.list_all()

    return [
        EvaluationListItemResponse(
            evaluation_id=run.id,
            model_name=run.model.name,
            model_version=run.model.version,
            dataset_name=run.dataset.name,
            tracking_run_id=run.mlflow_run_id,
            started_at=run.started_at.isoformat(),
            finished_at=run.finished_at.isoformat(),
            duration_ms=run.duration_ms,
        )
        for run in runs
    ]


@router.get(
    "/{evaluation_id}",
    response_model=EvaluationDetailResponse,
)
def get_evaluation(
    evaluation_id: str,
    repository: EvaluationRunRepository = Depends(get_evaluation_run_repository),
) -> EvaluationDetailResponse:
    """
    Return one persisted evaluation run.
    """

    run = repository.get(evaluation_id)

    if run is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evaluation not found",
        )

    return EvaluationDetailResponse(
        evaluation_id=run.id,
        model_name=run.model.name,
        model_version=run.model.version,
        dataset_name=run.dataset.name,
        tracking_run_id=run.mlflow_run_id,
        started_at=run.started_at.isoformat(),
        finished_at=run.finished_at.isoformat(),
        duration_ms=run.duration_ms,
        metrics=[
            EvaluationMetricResponse(
                name=metric.metric_type,
                value=metric.value,
                higher_is_better=(metric.higher_is_better),
            )
            for metric in run.metrics
        ],
    )
