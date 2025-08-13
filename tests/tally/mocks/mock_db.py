from peewee import SqliteDatabase
import pytest

from tally.models.db import ALL_MODELS


@pytest.fixture
def mock_db():
    test_db = SqliteDatabase(":memory:")

    test_db.bind(ALL_MODELS)
    test_db.connect()
    test_db.create_tables(ALL_MODELS)

    yield test_db

    test_db.drop_tables(ALL_MODELS)
    test_db.close()
