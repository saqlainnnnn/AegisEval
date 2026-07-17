from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from app.reports.builder import ReportBuilder
from app.services.report import ReportService


def test_build_evaluation_report() -> None:
    evaluation_repository = MagicMock()
    regression_repository = MagicMock()

    run = object()
    report = object()

    evaluation_repository.get.return_value = run

    builder = MagicMock(spec=ReportBuilder)
    builder.build_evaluation_report.return_value = report

    service = ReportService(
        evaluation_repository=evaluation_repository,
        regression_repository=regression_repository,
        builder=builder,
    )

    result = service.build_evaluation_report("run-1")

    assert result is report

    evaluation_repository.get.assert_called_once_with("run-1")

    builder.build_evaluation_report.assert_called_once_with(run)


def test_build_regression_report() -> None:
    evaluation_repository = MagicMock()
    regression_repository = MagicMock()

    run = object()
    report = object()

    regression_repository.get.return_value = run

    builder = MagicMock(spec=ReportBuilder)
    builder.build_regression_report.return_value = report

    service = ReportService(
        evaluation_repository=evaluation_repository,
        regression_repository=regression_repository,
        builder=builder,
    )

    result = service.build_regression_report(
        "regression-1"
    )

    assert result is report

    regression_repository.get.assert_called_once_with(
        "regression-1"
    )

    builder.build_regression_report.assert_called_once_with(
        run
    )


def test_missing_evaluation_report() -> None:
    evaluation_repository = MagicMock()
    regression_repository = MagicMock()

    evaluation_repository.get.return_value = None

    service = ReportService(
        evaluation_repository=evaluation_repository,
        regression_repository=regression_repository,
    )

    with pytest.raises(ValueError):
        service.build_evaluation_report("missing")


def test_missing_regression_report() -> None:
    evaluation_repository = MagicMock()
    regression_repository = MagicMock()

    regression_repository.get.return_value = None

    service = ReportService(
        evaluation_repository=evaluation_repository,
        regression_repository=regression_repository,
    )

    with pytest.raises(ValueError):
        service.build_regression_report("missing")