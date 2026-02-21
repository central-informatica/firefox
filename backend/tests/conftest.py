import os
import pytest
from unittest.mock import AsyncMock, patch
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from backend.app.main import app
from backend.app.db.session import get_db
from backend.app.db.models import Base

# -------------------------------------------------
# Carregar env de teste
# -------------------------------------------------
load_dotenv(".env.test")

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# -------------------------------------------------
# Mock service clients health checks for all tests
# -------------------------------------------------
@pytest.fixture(scope="session", autouse=True)
def mock_service_health_checks():
    """Mock health checks for Auth and Cofre services during tests."""
    with patch(
        "backend.app.services.auth_client.auth_client.health_check",
        new_callable=AsyncMock,
        return_value=True,
    ), patch(
        "backend.app.services.cofre_client.cofre_client.health_check",
        new_callable=AsyncMock,
        return_value=True,
    ):
        yield

# -------------------------------------------------
# Criar schema uma vez
# -------------------------------------------------
@pytest.fixture(scope="session", autouse=True)
def create_test_db():
    Base.metadata.create_all(bind=engine)
    yield

# -------------------------------------------------
# Sessão com rollback por teste
# -------------------------------------------------
@pytest.fixture
def db_session():
    connection = engine.connect()
    transaction = connection.begin()

    session = TestingSessionLocal(bind=connection)

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()

# -------------------------------------------------
# Override FastAPI dependency
# -------------------------------------------------
@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()
