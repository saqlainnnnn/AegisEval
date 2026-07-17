from app.datasets.csv_loader import CSVDatasetLoader


def test_load_csv_dataset(tmp_path) -> None:
    dataset_file = tmp_path / "dataset.csv"

    dataset_file.write_text(
        (
            "question,expected_answer\n"
            "What is AI?,Artificial Intelligence\n"
            "What is ML?,Machine Learning\n"
        ),
        encoding="utf-8",
    )

    loader = CSVDatasetLoader()

    dataset = loader.load(dataset_file)

    assert len(dataset.questions) == 2
    assert dataset.questions[0].question == "What is AI?"
    assert dataset.questions[1].expected_answer == "Machine Learning"


def test_parse_list() -> None:
    loader = CSVDatasetLoader()

    assert loader._parse_list("a,b,c") == [
        "a",
        "b",
        "c",
    ]

    assert loader._parse_list("") == []
