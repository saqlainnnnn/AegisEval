from app.database.base import Base
from app.database.engine import (
    create_database_engine,
)
from app.database.models.regression import (
    RegressionMetricRecord,
    RegressionRunRecord,
)


def test_regression_tables_are_created() -> None:
    engine = create_database_engine("sqlite+pysqlite:///:memory:")

    Base.metadata.create_all(engine)

    table_names = Base.metadata.tables.keys()

    assert RegressionRunRecord.__tablename__ in table_names

    assert RegressionMetricRecord.__tablename__ in table_names
