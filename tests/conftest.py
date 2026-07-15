# set up a clean, isolated SQLite test database and a FastAPI test client for every test run

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from shared.database import Base, get_db

# Import models so SQLAlchemy metadata is fully populated for create_all.
from CRM_Agent.model import ChatHistory, Complaint, Customer  # noqa: F401
from RAG_Agent.db_model import chunks, document  # noqa: F401
from Task_Agent.model import Task  # noqa: F401

TEST_DATABASE_URL = "sqlite:///./pytest_test.db"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app, raise_server_exceptions=False) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()