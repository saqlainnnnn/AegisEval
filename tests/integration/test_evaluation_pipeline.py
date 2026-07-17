import json

from app.adapters.dummy import DummyAdapter
from app.benchmark.runner import BenchmarkRunner
from app.datasets.factory import DatasetFactory
from app.domain.enums import MetricType, ModelType
from app.domain.evaluation import ModelConfig
from app.metrics.accuracy import AccuracyMetric
from app.metrics.engine import MetricsEngine
from app.metrics.failure_rate import FailureRateMetric
from app.metrics.latency import LatencyMetric


def test_complete_evaluation_pipeline(tmp_path) -> None:
    dataset_path = tmp_path / "evaluation_dataset.json"

    dataset_path.write_text(
        json.dumps(
            {
                "metadata": {
                    "name": "Integration Test Dataset",
                    "description": "Tests the complete evaluation pipeline",
                    "version": "1.0",
                },
                "questions": [
                    {
                        "question": "What is AI?",
                        "expected_answer": "Artificial Intelligence",
                    },
                    {
                        "question": "What is ML?",
                        "expected_answer": "Machine Learning",
                    },
                ],
            }
        ),
        encoding="utf-8",
    )

    loader = DatasetFactory.create(dataset_path)
    dataset = loader.load(dataset_path)

    config = ModelConfig(
        name="Dummy",
        version="1.0",
        model_type=ModelType.CUSTOM,
    )

    adapter = DummyAdapter(config)

    runner = BenchmarkRunner(adapter)
    evaluation = runner.run(dataset)

    metrics_engine = MetricsEngine(
        [
            AccuracyMetric(),
            LatencyMetric(),
            FailureRateMetric(),
        ]
    )

    summary = metrics_engine.compute(evaluation)

    assert len(dataset.questions) == 2

    assert len(evaluation.sample_results) == 2
    assert evaluation.model == config
    assert evaluation.dataset_id == str(dataset.id)

    assert len(summary.metrics) == 3

    assert summary.metrics[MetricType.ACCURACY].value == 1.0
    assert summary.metrics[MetricType.LATENCY].value >= 0
    assert summary.metrics[MetricType.FAILURE_RATE].value == 0.0
