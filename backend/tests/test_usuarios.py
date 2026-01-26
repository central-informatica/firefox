"""
Tests for usuarios module admin and IP validation.

Tests:
- Admin-only access for all endpoints
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
        "backend.app.api.routes.usuarios.auth_client.proxy_request",
        new_callable=AsyncMock
    ) as mock:
        # Default response for user operations
        mock.return_value = {
            "id": str(uuid.uuid4()),
            "email": "user@test.com",
            "first_name": "Test",
            "last_name": "User",
            "is_active": True,
        }
        yield mock


# ============================================
# GET /usuarios/ - List Users
# ============================================

def test_list_users_non_admin_forbidden(non_admin_client):
    """Test that non-admin user gets 403 Forbidden when listing users."""
    response = non_admin_client.get("/usuarios/")

    assert response.status_code == 403
    assert "administradores" in response.json()["detail"].lower()


def test_list_users_admin_success(admin_client, mock_auth_service):
    """Test that admin can list users."""
    mock_auth_service.return_value = [
        {"id": "1", "email": "user1@test.com"},
        {"id": "2", "email": "user2@test.com"},
    ]

    response = admin_client.get("/usuarios/")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_list_users_unauthenticated(client):
    """Test that unauthenticated request returns 401."""
    async def mock_auth():
        raise HTTPException(status_code=401, detail="Não autenticado")

    app.dependency_overrides[check_auth_with_ip] = mock_auth

    response = client.get("/usuarios/")

    app.dependency_overrides.pop(check_auth_with_ip, None)

    assert response.status_code == 401


# ============================================
# GET /usuarios/{user_id} - Get User
# ============================================

def test_get_user_non_admin_forbidden(non_admin_client):
    """Test that non-admin user gets 403 Forbidden when getting user."""
    fake_user_id = str(uuid.uuid4())

    response = non_admin_client.get(f"/usuarios/{fake_user_id}")

    assert response.status_code == 403
    assert "administradores" in response.json()["detail"].lower()


def test_get_user_admin_success(admin_client, mock_auth_service):
    """Test that admin can get user."""
    fake_user_id = str(uuid.uuid4())

    response = admin_client.get(f"/usuarios/{fake_user_id}")

    assert response.status_code == 200
    assert "id" in response.json()


# ============================================
# PUT /usuarios/{user_id} - Update User
# ============================================

def test_update_user_non_admin_forbidden(non_admin_client):
    """Test that non-admin user gets 403 Forbidden when updating user."""
    fake_user_id = str(uuid.uuid4())

    response = non_admin_client.put(
        f"/usuarios/{fake_user_id}",
        json={"first_name": "Updated"}
    )

    assert response.status_code == 403
    assert "administradores" in response.json()["detail"].lower()


def test_update_user_admin_success(admin_client, mock_auth_service):
    """Test that admin can update user."""
    fake_user_id = str(uuid.uuid4())
    mock_auth_service.return_value = {
        "id": fake_user_id,
        "email": "user@test.com",
        "first_name": "Updated",
    }

    response = admin_client.put(
        f"/usuarios/{fake_user_id}",
        json={"first_name": "Updated"}
    )

    assert response.status_code == 200


# ============================================
# DELETE /usuarios/{user_id} - Delete User
# ============================================

def test_delete_user_non_admin_forbidden(non_admin_client):
    """Test that non-admin user gets 403 Forbidden when deleting user."""
    fake_user_id = str(uuid.uuid4())

    response = non_admin_client.delete(f"/usuarios/{fake_user_id}")

    assert response.status_code == 403
    assert "administradores" in response.json()["detail"].lower()


def test_delete_user_admin_success(admin_client, mock_auth_service):
    """Test that admin can delete user."""
    fake_user_id = str(uuid.uuid4())
    mock_auth_service.return_value = {"message": "User deleted"}

    response = admin_client.delete(f"/usuarios/{fake_user_id}")

    assert response.status_code == 200
