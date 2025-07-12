import pytest
from fastapi.testclient import TestClient
from main import app
from sqlmodel import Session
from db_connect import engine,get_session



@pytest.fixture
def client():
    # Start a new connection and transaction
    connection = engine.connect()
    transaction = connection.begin()

    # Create a session bound to this transaction
    session = Session(bind=connection)

    # Override FastAPI dependency to use our test session
    def override_get_session():
        yield session

    app.dependency_overrides[get_session] = override_get_session

    with TestClient(app) as c:
        yield c  # run the actual test

    # Rollback changes after test
    session.close()
    transaction.rollback()
    connection.close()
