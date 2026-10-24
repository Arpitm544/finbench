import os
import sys
import pytest
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from finbench.config import settings
from finbench.database import Base, Transaction, init_db
from finbench.ingestion.download import ensure_dataset

TEST_DB_URL = "sqlite:///:memory:"


@pytest.fixture(scope="session")
def test_engine():
    engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    return engine


@pytest.fixture(scope="session")
def sample_df():
    csv_path = ensure_dataset(sample_records=2000)
    return pd.read_csv(csv_path)


@pytest.fixture
def db_session(test_engine):
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
