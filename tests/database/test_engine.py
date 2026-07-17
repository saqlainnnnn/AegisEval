from sqlalchemy import text

from app.database.engine import create_database_engine


def test_create_database_engine() -> None:
    engine = create_database_engine("sqlite+pysqlite:///:memory:")

    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))

        assert result.scalar_one() == 1
