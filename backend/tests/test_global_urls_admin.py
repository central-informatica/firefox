"""
Tests for global_urls module admin validation.

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
# GET /global-urls/empresa/{empresa_id} - List Global URLs
# ============================================

def test_list_global_urls_non_admin_forbidden(non_admin_client, empresa_id):
    """Test that non-admin user gets 403 Forbidden when listing global URLs."""
    response = non_admin_client.get(f"/global-urls/empresa/{empresa_id}")

    assert response.status_code == 403
    assert "administradores" in response.json()["detail"].lower()


# ============================================
# POST /global-urls/ - Create Global URL
# ============================================

def test_create_global_url_non_admin_forbidden(non_admin_client, empresa_id):
    """Test that non-admin user gets 403 Forbidden when creating a global URL."""
    response = non_admin_client.post(
        "/global-urls/",
        json={
            "url": "https://example.com",
            "empresa_id": empresa_id,
        }
    )

    assert response.status_code == 403
    assert "administradores" in response.json()["detail"].lower()


# ============================================
# GET /global-urls/id/{global_urls_id} - Get Global URL
# ============================================

def test_get_global_url_non_admin_forbidden(non_admin_client):
    """Test that non-admin user gets 403 Forbidden when getting a global URL."""
    fake_id = str(uuid.uuid4())

    response = non_admin_client.get(f"/global-urls/id/{fake_id}")

    assert response.status_code == 403
    assert "administradores" in response.json()["detail"].lower()


# ============================================
# PUT /global-urls/id/{global_urls_id} - Update Global URL
# ============================================

def test_update_global_url_non_admin_forbidden(non_admin_client):
    """Test that non-admin user gets 403 Forbidden when updating a global URL."""
    fake_id = str(uuid.uuid4())

    response = non_admin_client.put(
        f"/global-urls/id/{fake_id}",
        json={"url": "https://updated.com"}
    )

    assert response.status_code == 403
    assert "administradores" in response.json()["detail"].lower()


# ============================================
# DELETE /global-urls/id/{global_urls_id} - Delete Global URL
# ============================================

def test_delete_global_url_non_admin_forbidden(non_admin_client):
    """Test that non-admin user gets 403 Forbidden when deleting a global URL."""
    fake_id = str(uuid.uuid4())

    response = non_admin_client.delete(f"/global-urls/id/{fake_id}")

    assert response.status_code == 403
    assert "administradores" in response.json()["detail"].lower()
