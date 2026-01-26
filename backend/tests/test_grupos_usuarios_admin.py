"""
Tests for grupos_usuarios module admin validation.

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
# GET /grupos-usuarios/ - List All
# ============================================

def test_list_grupos_usuarios_non_admin_forbidden(non_admin_client):
    """Test that non-admin user gets 403 Forbidden when listing grupos-usuarios."""
    response = non_admin_client.get("/grupos-usuarios/")

    assert response.status_code == 403
    assert "administradores" in response.json()["detail"].lower()


# ============================================
# GET /grupos-usuarios/grupo/{grupo_id} - List by Grupo
# ============================================

def test_list_by_grupo_non_admin_forbidden(non_admin_client):
    """Test that non-admin user gets 403 Forbidden when listing grupos-usuarios by grupo."""
    fake_id = str(uuid.uuid4())

    response = non_admin_client.get(f"/grupos-usuarios/grupo/{fake_id}")

    assert response.status_code == 403
    assert "administradores" in response.json()["detail"].lower()


# ============================================
# GET /grupos-usuarios/{grupo_usuario_id} - Get One
# ============================================

def test_get_grupo_usuario_non_admin_forbidden(non_admin_client):
    """Test that non-admin user gets 403 Forbidden when getting a grupo-usuario."""
    fake_id = str(uuid.uuid4())

    response = non_admin_client.get(f"/grupos-usuarios/{fake_id}")

    assert response.status_code == 403
    assert "administradores" in response.json()["detail"].lower()


# ============================================
# POST /grupos-usuarios/ - Create
# ============================================

def test_create_grupo_usuario_non_admin_forbidden(non_admin_client):
    """Test that non-admin user gets 403 Forbidden when creating a grupo-usuario."""
    response = non_admin_client.post(
        "/grupos-usuarios/",
        json={
            "grupo_id": str(uuid.uuid4()),
            "usuario_id": str(uuid.uuid4()),
            "empresa_id": str(uuid.uuid4()),
        }
    )

    assert response.status_code == 403
    assert "administradores" in response.json()["detail"].lower()


# ============================================
# POST /grupos-usuarios/bulk - Create Bulk
# ============================================

def test_create_bulk_non_admin_forbidden(non_admin_client):
    """Test that non-admin user gets 403 Forbidden when creating grupos-usuarios in bulk."""
    response = non_admin_client.post(
        "/grupos-usuarios/bulk",
        json={
            "grupo_id": str(uuid.uuid4()),
            "usuario_ids": [str(uuid.uuid4()), str(uuid.uuid4())],
            "empresa_id": str(uuid.uuid4()),
        }
    )

    assert response.status_code == 403
    assert "administradores" in response.json()["detail"].lower()


# ============================================
# PUT /grupos-usuarios/{grupo_usuario_id} - Update
# ============================================

def test_update_grupo_usuario_non_admin_forbidden(non_admin_client):
    """Test that non-admin user gets 403 Forbidden when updating a grupo-usuario."""
    fake_id = str(uuid.uuid4())

    response = non_admin_client.put(
        f"/grupos-usuarios/{fake_id}",
        json={"grupo_id": str(uuid.uuid4())}
    )

    assert response.status_code == 403
    assert "administradores" in response.json()["detail"].lower()


# ============================================
# DELETE /grupos-usuarios/{grupo_usuario_id} - Delete
# ============================================

def test_delete_grupo_usuario_non_admin_forbidden(non_admin_client):
    """Test that non-admin user gets 403 Forbidden when deleting a grupo-usuario."""
    fake_id = str(uuid.uuid4())

    response = non_admin_client.delete(f"/grupos-usuarios/{fake_id}")

    assert response.status_code == 403
    assert "administradores" in response.json()["detail"].lower()
