"""
Tests for grupos_certificados_urls module admin validation.

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
# GET /grupos-certificados/{grupo_cert_id}/urls - List URLs
# ============================================

def test_list_urls_non_admin_forbidden(non_admin_client):
    """Test that non-admin user gets 403 Forbidden when listing grupo-certificado URLs."""
    fake_id = str(uuid.uuid4())

    response = non_admin_client.get(f"/grupos-certificados/{fake_id}/urls")

    assert response.status_code == 403
    assert "administradores" in response.json()["detail"].lower()


# ============================================
# POST /grupos-certificados/{grupo_cert_id}/urls - Add URL
# ============================================

def test_add_url_non_admin_forbidden(non_admin_client):
    """Test that non-admin user gets 403 Forbidden when adding a URL to grupo-certificado."""
    fake_id = str(uuid.uuid4())

    response = non_admin_client.post(
        f"/grupos-certificados/{fake_id}/urls",
        json={
            "global_urls_id": str(uuid.uuid4()),
        }
    )

    assert response.status_code == 403
    assert "administradores" in response.json()["detail"].lower()


# ============================================
# DELETE /grupos-certificados-urls/{grupo_cert_url_id} - Remove URL
# ============================================

def test_remove_url_non_admin_forbidden(non_admin_client):
    """Test that non-admin user gets 403 Forbidden when removing a URL from grupo-certificado."""
    fake_id = str(uuid.uuid4())

    response = non_admin_client.delete(f"/grupos-certificados-urls/{fake_id}")

    assert response.status_code == 403
    assert "administradores" in response.json()["detail"].lower()
