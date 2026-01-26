"""
Tests for ramos module admin validation.

Tests verify that non-admin users receive 403 Forbidden for all endpoints.
"""

import uuid

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.api.deps import check_auth_with_ip
from backend.app.db.session import get_db

from tests.factories.usuarios_ip_whitelist_factory import criar_usuarios_ip_whitelist


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


@pytest.fixture
def user_id():
    return str(uuid.uuid4())


@pytest.fixture
def empresa_id():
    return str(uuid.uuid4())


@pytest.fixture
def non_admin_client(db_session, user_id, empresa_id):
    """Test client with non-admin user and whitelisted IP."""
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


# ============================================
# GET /ramos/ - List Ramos
# ============================================

def test_list_ramos_non_admin_forbidden(non_admin_client):
    """Test that non-admin user gets 403 Forbidden when listing ramos."""
    response = non_admin_client.get("/ramos/")

    assert response.status_code == 403
    assert "administradores" in response.json()["detail"].lower()


# ============================================
# GET /ramos/paginado - List Ramos Paginated
# ============================================

def test_list_ramos_paginado_non_admin_forbidden(non_admin_client):
    """Test that non-admin user gets 403 Forbidden when listing ramos paginated."""
    response = non_admin_client.get("/ramos/paginado")

    assert response.status_code == 403
    assert "administradores" in response.json()["detail"].lower()


# ============================================
# POST /ramos/ - Create Ramo
# ============================================

def test_create_ramo_non_admin_forbidden(non_admin_client):
    """Test that non-admin user gets 403 Forbidden when creating a ramo."""
    response = non_admin_client.post(
        "/ramos/",
        json={
            "ramo": "Test Ramo",
        }
    )

    assert response.status_code == 403
    assert "administradores" in response.json()["detail"].lower()


# ============================================
# GET /ramos/id/{ramos_id} - Get Ramo
# ============================================

def test_get_ramo_non_admin_forbidden(non_admin_client):
    """Test that non-admin user gets 403 Forbidden when getting a ramo."""
    fake_id = str(uuid.uuid4())

    response = non_admin_client.get(f"/ramos/id/{fake_id}")

    assert response.status_code == 403
    assert "administradores" in response.json()["detail"].lower()


# ============================================
# PUT /ramos/id/{ramos_id} - Update Ramo
# ============================================

def test_update_ramo_non_admin_forbidden(non_admin_client):
    """Test that non-admin user gets 403 Forbidden when updating a ramo."""
    fake_id = str(uuid.uuid4())

    response = non_admin_client.put(
        f"/ramos/id/{fake_id}",
        json={"nome": "Updated Ramo"}
    )

    assert response.status_code == 403
    assert "administradores" in response.json()["detail"].lower()


# ============================================
# DELETE /ramos/id/{ramos_id} - Delete Ramo
# ============================================

def test_delete_ramo_non_admin_forbidden(non_admin_client):
    """Test that non-admin user gets 403 Forbidden when deleting a ramo."""
    fake_id = str(uuid.uuid4())

    response = non_admin_client.delete(f"/ramos/id/{fake_id}")

    assert response.status_code == 403
    assert "administradores" in response.json()["detail"].lower()
