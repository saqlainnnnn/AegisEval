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
from app.metrics.retrieval.mrr import MRRMetric


def test_mrr_metric_returns_one() -> None:
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

    metric = MRRMetric(k=5).compute(evaluation)

    assert metric.metric == MetricType.MRR
    assert metric.value == 1.0


def test_mrr_metric_second_position() -> None:
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
        RetrievedDocument(id="doc2", content="2"),
        RetrievedDocument(id="doc1", content="1"),
    ]

    metric = MRRMetric(k=5).compute(evaluation)

    assert metric.value == 0.5


def test_mrr_metric_no_match() -> None:
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
        RetrievedDocument(id="doc2", content="2"),
        RetrievedDocument(id="doc3", content="3"),
    ]

    metric = MRRMetric(k=5).compute(evaluation)

    assert metric.value == 0.0