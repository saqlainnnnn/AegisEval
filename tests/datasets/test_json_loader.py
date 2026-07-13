import json

from app.datasets.json_loader import JSONDatasetLoader


def test_load_json_dataset(tmp_path) -> None:
    dataset_file = tmp_path / "dataset.json"

    dataset_file.write_text(
        json.dumps(
            {
                "metadata": {
                    "name": "Medical QA",
                    "description": "Test dataset",
                },
                "questions": [
                    {
                        "question": "What is AI?",
                        "expected_answer": "Artificial Intelligence",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    loader = JSONDatasetLoader()

    dataset = loader.load(dataset_file)

    assert dataset.metadata.name == "Medical QA"
    assert len(dataset.questions) == 1
    assert dataset.questions[0].question == "What is AI?"