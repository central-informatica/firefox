"""
Tests for grupos module admin validation.

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
# GET /grupos/empresa/{empresa_id} - List Grupos by Empresa
# ============================================

def test_list_grupos_empresa_non_admin_forbidden(non_admin_client, empresa_id):
    """Test that non-admin user gets 403 Forbidden when listing grupos by empresa."""
    response = non_admin_client.get(f"/grupos/empresa/{empresa_id}")

    assert response.status_code == 403
    assert "administradores" in response.json()["detail"].lower()


# ============================================
# GET /grupos/{grupo_id} - Get Grupo
# ============================================

def test_get_grupo_non_admin_forbidden(non_admin_client):
    """Test that non-admin user gets 403 Forbidden when getting a grupo."""
    fake_id = str(uuid.uuid4())

    response = non_admin_client.get(f"/grupos/{fake_id}")

    assert response.status_code == 403
    assert "administradores" in response.json()["detail"].lower()


# ============================================
# POST /grupos/ - Create Grupo
# ============================================

def test_create_grupo_non_admin_forbidden(non_admin_client, empresa_id):
    """Test that non-admin user gets 403 Forbidden when creating a grupo."""
    response = non_admin_client.post(
        "/grupos/",
        json={
            "nome": "Test Group",
            "empresa_id": empresa_id,
            "plano_id": str(uuid.uuid4()),
        }
    )

    assert response.status_code == 403
    assert "administradores" in response.json()["detail"].lower()


# ============================================
# PUT /grupos/{grupo_id} - Update Grupo
# ============================================

def test_update_grupo_non_admin_forbidden(non_admin_client):
    """Test that non-admin user gets 403 Forbidden when updating a grupo."""
    fake_id = str(uuid.uuid4())

    response = non_admin_client.put(
        f"/grupos/{fake_id}",
        json={"nome": "Updated Group"}
    )

    assert response.status_code == 403
    assert "administradores" in response.json()["detail"].lower()


# ============================================
# DELETE /grupos/{grupo_id} - Delete Grupo
# ============================================

def test_delete_grupo_non_admin_forbidden(non_admin_client):
    """Test that non-admin user gets 403 Forbidden when deleting a grupo."""
    fake_id = str(uuid.uuid4())

    response = non_admin_client.delete(f"/grupos/{fake_id}")

    assert response.status_code == 403
    assert "administradores" in response.json()["detail"].lower()


# ============================================
# GET /grupos/{grupo_id}/certificados - List Certificados
# ============================================

def test_list_certificados_grupo_non_admin_forbidden(non_admin_client):
    """Test that non-admin user gets 403 Forbidden when listing certificados of a grupo."""
    fake_id = str(uuid.uuid4())

    response = non_admin_client.get(f"/grupos/{fake_id}/certificados")

    assert response.status_code == 403
    assert "administradores" in response.json()["detail"].lower()


# ============================================
# POST /grupos/{grupo_id}/certificados - Add Certificado
# ============================================

def test_add_certificado_grupo_non_admin_forbidden(non_admin_client, empresa_id):
    """Test that non-admin user gets 403 Forbidden when adding a certificado to a grupo."""
    fake_id = str(uuid.uuid4())

    response = non_admin_client.post(
        f"/grupos/{fake_id}/certificados",
        json={
            "certificado_id": str(uuid.uuid4()),
            "empresa_id": empresa_id,
        }
    )

    assert response.status_code == 403
    assert "administradores" in response.json()["detail"].lower()


# ============================================
# DELETE /grupos/{grupo_id}/certificados - Remove Certificado
# ============================================

def test_remove_certificado_grupo_non_admin_forbidden(non_admin_client, empresa_id):
    """Test that non-admin user gets 403 Forbidden when removing a certificado from a grupo."""
    fake_id = str(uuid.uuid4())

    response = non_admin_client.request(
        "DELETE",
        f"/grupos/{fake_id}/certificados",
        json={
            "certificado_id": str(uuid.uuid4()),
            "empresa_id": empresa_id,
        }
    )

    assert response.status_code == 403
    assert "administradores" in response.json()["detail"].lower()


# ============================================
# GET /grupos/{grupo_id}/usuarios - List Usuarios
# ============================================

def test_list_usuarios_grupo_non_admin_forbidden(non_admin_client):
    """Test that non-admin user gets 403 Forbidden when listing usuarios of a grupo."""
    fake_id = str(uuid.uuid4())

    response = non_admin_client.get(f"/grupos/{fake_id}/usuarios")

    assert response.status_code == 403
    assert "administradores" in response.json()["detail"].lower()


# ============================================
# POST /grupos/{grupo_id}/usuarios - Add Usuario
# ============================================

def test_add_usuario_grupo_non_admin_forbidden(non_admin_client, empresa_id):
    """Test that non-admin user gets 403 Forbidden when adding a usuario to a grupo."""
    fake_id = str(uuid.uuid4())

    response = non_admin_client.post(
        f"/grupos/{fake_id}/usuarios",
        json={
            "usuario_id": str(uuid.uuid4()),
            "empresa_id": empresa_id,
        }
    )

    assert response.status_code == 403
    assert "administradores" in response.json()["detail"].lower()


# ============================================
# DELETE /grupos/{grupo_id}/usuarios/{usuario_id} - Remove Usuario
# ============================================

def test_remove_usuario_grupo_non_admin_forbidden(non_admin_client):
    """Test that non-admin user gets 403 Forbidden when removing a usuario from a grupo."""
    fake_grupo_id = str(uuid.uuid4())
    fake_usuario_id = str(uuid.uuid4())

    response = non_admin_client.delete(f"/grupos/{fake_grupo_id}/usuarios/{fake_usuario_id}")

    assert response.status_code == 403
    assert "administradores" in response.json()["detail"].lower()


# ============================================
# POST /grupos/{grupo_id}/usuarios/bulk - Add Usuarios Bulk
# ============================================

def test_add_usuarios_bulk_non_admin_forbidden(non_admin_client, empresa_id):
    """Test that non-admin user gets 403 Forbidden when adding usuarios in bulk to a grupo."""
    fake_id = str(uuid.uuid4())

    response = non_admin_client.post(
        f"/grupos/{fake_id}/usuarios/bulk",
        json={
            "grupo_id": fake_id,
            "usuario_ids": [str(uuid.uuid4()), str(uuid.uuid4())],
            "empresa_id": empresa_id,
        }
    )

    assert response.status_code == 403
    assert "administradores" in response.json()["detail"].lower()
