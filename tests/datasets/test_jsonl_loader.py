import json

from app.datasets.jsonl_loader import JSONLDatasetLoader


def test_load_jsonl_dataset(tmp_path) -> None:
    dataset_file = tmp_path / "dataset.jsonl"

    samples = [
        {
            "question": "What is AI?",
            "expected_answer": "Artificial Intelligence",
        },
        {
            "question": "What is ML?",
            "expected_answer": "Machine Learning",
        },
    ]

    with dataset_file.open(
        "w",
        encoding="utf-8",
    ) as file:

        for sample in samples:
            file.write(
                json.dumps(sample)
            )
            file.write("\n")

    loader = JSONLDatasetLoader()

    dataset = loader.load(dataset_file)

    assert len(dataset.questions) == 2
    assert dataset.questions[1].question == "What is ML?"