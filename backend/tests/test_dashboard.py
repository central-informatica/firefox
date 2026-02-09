"""
Tests for dashboard routes.
"""

import uuid
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.api.deps import check_auth_with_ip
from backend.app.db.session import get_db

from tests.factories.certificado_factory import criar_certificado


# ============================================
# HELPER FUNCTIONS
# ============================================

def _mock_user_data(user_id: str, org_id: str, is_admin: bool = True, ip: str = "127.0.0.1"):
    """Create mock user data dict as returned by auth service."""
    return {
        "id": user_id,
        "usuario_id": user_id,
        "organization_id": org_id,
        "is_admin": is_admin,
        "email": "user@test.com",
        "ip_address": ip,
    }


# ============================================
# FIXTURES
# ============================================

@pytest.fixture
def user_id():
    """Generate a test user ID."""
    return str(uuid.uuid4())


@pytest.fixture
def organization_id():
    """Generate a test organization ID."""
    return str(uuid.uuid4())


@pytest.fixture
def empresa_id():
    """Generate a test empresa ID."""
    return str(uuid.uuid4())


@pytest.fixture
def admin_client(db_session, user_id, organization_id):
    """Test client with admin user."""
    async def mock_auth():
        return _mock_user_data(user_id, organization_id, is_admin=True)

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[check_auth_with_ip] = mock_auth
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def mock_auth_service():
    """Mock auth_client.proxy_request to avoid external calls."""
    with patch(
        "backend.app.api.routes.dashboard.auth_client.proxy_request",
        new_callable=AsyncMock
    ) as mock:
        # Default response for user count
        mock.return_value = {"total": 10}
        yield mock


# ============================================
# GET /dashboard/stats - Get Dashboard Stats
# ============================================

def test_dashboard_stats_success(admin_client, db_session, empresa_id, mock_auth_service):
    """Test that admin can get dashboard stats."""
    # Create some test certificates
    criar_certificado(db_session, empresa_id=empresa_id, ativo=True)
    criar_certificado(db_session, empresa_id=empresa_id, ativo=True)
    criar_certificado(db_session, empresa_id=empresa_id, ativo=False)

    db_session.commit()

    # Mock auth service response
    mock_auth_service.return_value = {"total": 5}

    response = admin_client.get(
        "/dashboard/stats",
        cookies={"session_token": "fake_token"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "total_usuarios" in data
    assert "certificados_ativos" in data
    assert data["total_usuarios"] == 5
    assert data["certificados_ativos"] == 2  # Only active certificates


def test_dashboard_stats_auth_service_error(admin_client, db_session, empresa_id, mock_auth_service):
    """Test that dashboard returns 0 users when auth service fails."""
    # Create some test certificates
    criar_certificado(db_session, empresa_id=empresa_id, ativo=True)
    db_session.commit()

    # Mock auth service to raise error
    from backend.app.core.exceptions import AuthServiceError
    mock_auth_service.side_effect = AuthServiceError("Auth service unavailable")

    response = admin_client.get(
        "/dashboard/stats",
        cookies={"session_token": "fake_token"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total_usuarios"] == 0  # Should return 0 on error
    assert data["certificados_ativos"] == 1


def test_dashboard_stats_missing_session_token(admin_client, db_session):
    """Test that missing session token returns 401."""
    response = admin_client.get("/dashboard/stats")

    assert response.status_code == 401
    assert "Session token not found" in response.json()["detail"]


def test_dashboard_stats_missing_organization_id(db_session):
    """Test that missing organization_id returns 400."""
    async def mock_auth_no_org():
        return {
            "id": str(uuid.uuid4()),
            "email": "user@test.com",
            "is_admin": True,
        }

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[check_auth_with_ip] = mock_auth_no_org
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as client:
        response = client.get(
            "/dashboard/stats",
            cookies={"session_token": "fake_token"}
        )

    app.dependency_overrides.clear()

    assert response.status_code == 400
    assert "Organization ID not found" in response.json()["detail"]
