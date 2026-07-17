from sqlalchemy import text

from app.database.engine import create_database_engine
from app.database.session import create_session_factory


def test_create_session_factory() -> None:
    engine = create_database_engine("sqlite+pysqlite:///:memory:")

    session_factory = create_session_factory(engine)

    with session_factory() as session:
        result = session.execute(text("SELECT 1"))

        assert result.scalar_one() == 1
