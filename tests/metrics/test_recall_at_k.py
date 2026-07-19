from app.adapters.dummy import DummyAdapter
from app.benchmark.runner import BenchmarkRunner
from app.domain.dataset import (
    Dataset,
    DatasetMetadata,
    Question,
    RelevantDocument,
)
from app.domain.enums import MetricType, ModelType
from app.domain.evaluation import ModelConfig
from app.domain.prediction import RetrievedDocument
from app.metrics.retrieval.recall_at_k import RecallMetric


def test_recall_metric_returns_one() -> None:
    dataset = Dataset(
        metadata=DatasetMetadata(
            name="Retrieval Test",
            description="Recall Test",
        ),
        questions=[
            Question(
                question="Q1",
                expected_answer="A1",
                expected_documents=[
                    RelevantDocument(
                        id="doc1",
                        content="Document 1",
                    ),
                    RelevantDocument(
                        id="doc2",
                        content="Document 2",
                    ),
                ],
            ),
        ],
    )

    adapter = DummyAdapter(
        ModelConfig(
            name="Dummy",
            version="1.0",
            model_type=ModelType.CUSTOM,
        )
    )

    evaluation = BenchmarkRunner(adapter).run(dataset)

    metric = RecallMetric(k=5).compute(evaluation)

    assert metric.metric == MetricType.RECALL_AT_K
    assert metric.value == 1.0


def test_recall_metric_respects_k() -> None:
    dataset = Dataset(
        metadata=DatasetMetadata(
            name="Retrieval Test",
            description="Recall Test",
        ),
        questions=[
            Question(
                question="Q1",
                expected_answer="A1",
                expected_documents=[
                    RelevantDocument(id="doc1", content="1"),
                    RelevantDocument(id="doc2", content="2"),
                    RelevantDocument(id="doc3", content="3"),
                ],
            ),
        ],
    )

    adapter = DummyAdapter(
        ModelConfig(
            name="Dummy",
            version="1.0",
            model_type=ModelType.CUSTOM,
        )
    )

    evaluation = BenchmarkRunner(adapter).run(dataset)

    evaluation.sample_results[0].prediction.retrieved_documents = [
        RetrievedDocument(id="doc1", content="1"),
        RetrievedDocument(id="doc4", content="4"),
        RetrievedDocument(id="doc2", content="2"),
    ]

    metric = RecallMetric(k=2).compute(evaluation)

    assert metric.value == 1 / 3