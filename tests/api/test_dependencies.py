from app.api.dependencies import (
    get_database_engine,
    get_database_session,
    get_session_factory,
)
from app.core.config import get_settings


def test_get_settings() -> None:
    settings = get_settings()

    assert settings.app_name == "AegisEval"
    assert settings.app_version == "0.1.0"

    assert settings.database_url


def test_database_engine_is_cached() -> None:
    first_engine = get_database_engine()
    second_engine = get_database_engine()

    assert first_engine is second_engine


def test_session_factory_is_cached() -> None:
    first_factory = get_session_factory()
    second_factory = get_session_factory()

    assert first_factory is second_factory


def test_database_session_dependency() -> None:
    dependency = get_database_session()

    session = next(dependency)

    try:
        assert session is not None

    finally:
        dependency.close()