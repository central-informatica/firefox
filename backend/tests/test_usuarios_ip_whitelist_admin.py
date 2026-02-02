"""
Tests for usuarios_ip_whitelist module admin validation.

Tests verify that non-admin users receive 403 Forbidden for all endpoints.
"""

import uuid

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.api.deps import check_auth_with_ip, check_auth
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
    app.dependency_overrides[check_auth] = mock_auth  # POST endpoint uses check_auth
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


# ============================================
# GET /usuarios-ip-whitelist/empresa/{empresa_id} - List by Empresa
# ============================================

def test_list_by_empresa_non_admin_forbidden(non_admin_client, empresa_id):
    """Test that non-admin user gets 403 Forbidden when listing IP whitelist by empresa."""
    response = non_admin_client.get(f"/usuarios-ip-whitelist/empresa/{empresa_id}")

    assert response.status_code == 403
    assert "administradores" in response.json()["detail"].lower()


# ============================================
# GET /usuarios-ip-whitelist/usuario/{usuario_id} - List by Usuario
# ============================================

def test_list_by_usuario_non_admin_forbidden(non_admin_client, user_id):
    """Test that non-admin user gets 403 Forbidden when listing IP whitelist by usuario."""
    response = non_admin_client.get(f"/usuarios-ip-whitelist/usuario/{user_id}")

    assert response.status_code == 403
    assert "administradores" in response.json()["detail"].lower()


# ============================================
# GET /usuarios-ip-whitelist/{whitelist_id} - Get Whitelist Entry
# ============================================

def test_get_whitelist_non_admin_forbidden(non_admin_client):
    """Test that non-admin user gets 403 Forbidden when getting a whitelist entry."""
    fake_id = str(uuid.uuid4())

    response = non_admin_client.get(f"/usuarios-ip-whitelist/{fake_id}")

    assert response.status_code == 403
    assert "administradores" in response.json()["detail"].lower()


# ============================================
# POST /usuarios-ip-whitelist/ - Create Whitelist Entry
# ============================================

def test_create_whitelist_non_admin_forbidden(non_admin_client, empresa_id, user_id):
    """Test that non-admin user gets 403 Forbidden when creating a whitelist entry."""
    response = non_admin_client.post(
        "/usuarios-ip-whitelist/",
        json={
            "usuario_id": str(uuid.uuid4()),
            "empresa_id": empresa_id,
            "ip_address": "192.168.1.100",
        }
    )

    assert response.status_code == 403
    assert "administradores" in response.json()["detail"].lower()


# ============================================
# PUT /usuarios-ip-whitelist/{whitelist_id} - Update Whitelist Entry
# ============================================

def test_update_whitelist_non_admin_forbidden(non_admin_client):
    """Test that non-admin user gets 403 Forbidden when updating a whitelist entry."""
    fake_id = str(uuid.uuid4())

    response = non_admin_client.put(
        f"/usuarios-ip-whitelist/{fake_id}",
        json={"ip_address": "192.168.1.200"}
    )

    assert response.status_code == 403
    assert "administradores" in response.json()["detail"].lower()


# ============================================
# DELETE /usuarios-ip-whitelist/{whitelist_id} - Delete Whitelist Entry
# ============================================

def test_delete_whitelist_non_admin_forbidden(non_admin_client):
    """Test that non-admin user gets 403 Forbidden when deleting a whitelist entry."""
    fake_id = str(uuid.uuid4())

    response = non_admin_client.delete(f"/usuarios-ip-whitelist/{fake_id}")

    assert response.status_code == 403
    assert "administradores" in response.json()["detail"].lower()


# ============================================
# DELETE /usuarios-ip-whitelist/usuario/{usuario_id} - Delete All by Usuario
# ============================================

def test_delete_all_by_usuario_non_admin_forbidden(non_admin_client):
    """Test that non-admin user gets 403 Forbidden when deleting all entries by usuario."""
    fake_user_id = str(uuid.uuid4())

    response = non_admin_client.delete(f"/usuarios-ip-whitelist/usuario/{fake_user_id}")

    assert response.status_code == 403
    assert "administradores" in response.json()["detail"].lower()
