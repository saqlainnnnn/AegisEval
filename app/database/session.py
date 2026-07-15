from __future__ import annotations

from sqlalchemy import Engine
from sqlalchemy.orm import Session, sessionmaker


def create_session_factory(
    engine: Engine,
) -> sessionmaker[Session]:
    """
    Create a SQLAlchemy session factory.
    """

    return sessionmaker(
        bind=engine,
        class_=Session,
        expire_on_commit=False,
    )