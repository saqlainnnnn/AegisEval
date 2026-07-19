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
from app.metrics.retrieval.map import MAPMetric


def test_map_metric_returns_one() -> None:
    dataset = Dataset(
        metadata=DatasetMetadata(
            name="Test",
            description="Test",
        ),
        questions=[
            Question(
                question="Q",
                expected_answer="A",
                expected_documents=[
                    RelevantDocument(id="doc1", content="1"),
                    RelevantDocument(id="doc2", content="2"),
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

    metric = MAPMetric(k=5).compute(evaluation)

    assert metric.metric == MetricType.MAP
    assert metric.value == 1.0


def test_map_metric_partial() -> None:
    dataset = Dataset(
        metadata=DatasetMetadata(
            name="Test",
            description="Test",
        ),
        questions=[
            Question(
                question="Q",
                expected_answer="A",
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

    metric = MAPMetric(k=5).compute(evaluation)

    expected_ap = (1.0 + (2 / 3)) / 3

    assert metric.value == expected_ap