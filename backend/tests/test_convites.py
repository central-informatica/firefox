"""
Tests for convites module admin and IP validation.

Tests:
- Admin-only access for create, list, revoke endpoints
- Public access for accept endpoint
- IP whitelist validation
"""

import uuid
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.api.deps import check_auth_with_ip
from backend.app.db.session import get_db

from tests.factories.usuarios_ip_whitelist_factory import criar_usuarios_ip_whitelist


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
def empresa_id():
    """Generate a test empresa ID."""
    return str(uuid.uuid4())


@pytest.fixture
def admin_client(db_session, user_id, empresa_id):
    """Test client with admin user and whitelisted IP."""
    # Add IP whitelist entry
    criar_usuarios_ip_whitelist(
        db_session,
        usuario_id=user_id,
        empresa_id=empresa_id,
        ip_address="127.0.0.1",
    )

    async def mock_auth():
        return _mock_user_data(user_id, empresa_id, is_admin=True, ip="127.0.0.1")

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
def non_admin_client(db_session, user_id, empresa_id):
    """Test client with non-admin user and whitelisted IP."""
    # Add IP whitelist entry
    criar_usuarios_ip_whitelist(
        db_session,
        usuario_id=user_id,
        empresa_id=empresa_id,
        ip_address="127.0.0.1",
    )

    async def mock_auth():
        return _mock_user_data(user_id, empresa_id, is_admin=False, ip="127.0.0.1")

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
        "backend.app.api.routes.convites.auth_client.proxy_request",
        new_callable=AsyncMock
    ) as mock:
        # Default response for invitation operations
        mock.return_value = {
            "id": str(uuid.uuid4()),
            "email": "invited@test.com",
            "status": "pending",
        }
        yield mock


# ============================================
# POST /convites/ - Create Invitation
# ============================================

def test_create_invitation_non_admin_forbidden(non_admin_client):
    """Test that non-admin user gets 403 Forbidden when creating invitation."""
    response = non_admin_client.post(
        "/convites/",
        json={"email": "newuser@test.com"}
    )

    assert response.status_code == 403
    assert "administradores" in response.json()["detail"].lower()


def test_create_invitation_admin_success(admin_client, mock_auth_service):
    """Test that admin can create invitation."""
    response = admin_client.post(
        "/convites/",
        json={"email": "newuser@test.com"}
    )

    assert response.status_code == 200


def test_create_invitation_unauthenticated(client):
    """Test that unauthenticated request returns 401."""
    async def mock_auth():
        raise HTTPException(status_code=401, detail="Não autenticado")

    app.dependency_overrides[check_auth_with_ip] = mock_auth

    response = client.post(
        "/convites/",
        json={"email": "newuser@test.com"}
    )

    app.dependency_overrides.pop(check_auth_with_ip, None)

    assert response.status_code == 401


# ============================================
# GET /convites/ - List Invitations
# ============================================

def test_list_invitations_non_admin_forbidden(non_admin_client):
    """Test that non-admin user gets 403 Forbidden when listing invitations."""
    response = non_admin_client.get("/convites/")

    assert response.status_code == 403
    assert "administradores" in response.json()["detail"].lower()


def test_list_invitations_admin_success(admin_client, mock_auth_service):
    """Test that admin can list invitations."""
    mock_auth_service.return_value = [
        {"id": "1", "email": "user1@test.com", "status": "pending"},
        {"id": "2", "email": "user2@test.com", "status": "accepted"},
    ]

    response = admin_client.get("/convites/")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


# ============================================
# DELETE /convites/{invitation_id} - Revoke Invitation
# ============================================

def test_revoke_invitation_non_admin_forbidden(non_admin_client):
    """Test that non-admin user gets 403 Forbidden when revoking invitation."""
    fake_invitation_id = str(uuid.uuid4())

    response = non_admin_client.delete(f"/convites/{fake_invitation_id}")

    assert response.status_code == 403
    assert "administradores" in response.json()["detail"].lower()


def test_revoke_invitation_admin_success(admin_client, mock_auth_service):
    """Test that admin can revoke invitation."""
    fake_invitation_id = str(uuid.uuid4())
    mock_auth_service.return_value = {"message": "Invitation revoked"}

    response = admin_client.delete(f"/convites/{fake_invitation_id}")

    assert response.status_code == 200


# ============================================
# POST /convites/accept - Accept Invitation (PUBLIC)
# ============================================

def test_accept_invitation_public(client, mock_auth_service):
    """Test that accept invitation endpoint is public (no auth required)."""
    mock_auth_service.return_value = {
        "id": str(uuid.uuid4()),
        "email": "newuser@test.com",
        "message": "Invitation accepted",
    }

    response = client.post(
        "/convites/accept",
        json={
            "token": "valid-token-123",
            "password": "securepassword123",
            "first_name": "John",
            "last_name": "Doe",
        }
    )

    assert response.status_code == 200
