from __future__ import annotations

from collections.abc import Generator
from functools import lru_cache

from sqlalchemy import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import Settings, get_settings
from app.database.engine import create_database_engine
from app.database.session import create_session_factory


@lru_cache
def get_database_engine() -> Engine:
    """
    Create and cache the application database engine.
    """

    settings = get_settings()

    return create_database_engine(
        settings.database_url
    )


@lru_cache
def get_session_factory() -> sessionmaker[Session]:
    """
    Create and cache the application session factory.
    """

    engine = get_database_engine()

    return create_session_factory(
        engine
    )


def get_database_session() -> Generator[Session, None, None]:
    """
    Provide a database session for one request.
    """

    session_factory = get_session_factory()

    with session_factory() as session:
        yield session