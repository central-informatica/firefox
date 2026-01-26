"""
Tests for planos_trabalho module admin validation.

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
# GET /planos-trabalho/ - List Planos
# ============================================

def test_list_planos_non_admin_forbidden(non_admin_client):
    """Test that non-admin user gets 403 Forbidden when listing planos de trabalho."""
    response = non_admin_client.get("/planos-trabalho/")

    assert response.status_code == 403
    assert "administradores" in response.json()["detail"].lower()


# ============================================
# GET /planos-trabalho/{plano_id} - Get Plano
# ============================================

def test_get_plano_non_admin_forbidden(non_admin_client):
    """Test that non-admin user gets 403 Forbidden when getting a plano de trabalho."""
    fake_id = str(uuid.uuid4())

    response = non_admin_client.get(f"/planos-trabalho/{fake_id}")

    assert response.status_code == 403
    assert "administradores" in response.json()["detail"].lower()


# ============================================
# POST /planos-trabalho/ - Create Plano
# ============================================

def test_create_plano_non_admin_forbidden(non_admin_client, empresa_id):
    """Test that non-admin user gets 403 Forbidden when creating a plano de trabalho."""
    response = non_admin_client.post(
        "/planos-trabalho/",
        json={
            "nome": "Test Plan",
            "descricao": "Test description",
        }
    )

    assert response.status_code == 403
    assert "administradores" in response.json()["detail"].lower()


# ============================================
# PUT /planos-trabalho/{plano_id} - Update Plano
# ============================================

def test_update_plano_non_admin_forbidden(non_admin_client):
    """Test that non-admin user gets 403 Forbidden when updating a plano de trabalho."""
    fake_id = str(uuid.uuid4())

    response = non_admin_client.put(
        f"/planos-trabalho/{fake_id}",
        json={"nome": "Updated Plan"}
    )

    assert response.status_code == 403
    assert "administradores" in response.json()["detail"].lower()


# ============================================
# DELETE /planos-trabalho/{plano_id} - Delete Plano
# ============================================

def test_delete_plano_non_admin_forbidden(non_admin_client):
    """Test that non-admin user gets 403 Forbidden when deleting a plano de trabalho."""
    fake_id = str(uuid.uuid4())

    response = non_admin_client.delete(f"/planos-trabalho/{fake_id}")

    assert response.status_code == 403
    assert "administradores" in response.json()["detail"].lower()
