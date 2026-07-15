from __future__ import annotations

from sqlalchemy import Engine, create_engine


def create_database_engine(
    database_url: str,
    *,
    echo: bool = False,
) -> Engine:
    """
    Create a SQLAlchemy database engine.
    """

    return create_engine(
        database_url,
        echo=echo,
    )