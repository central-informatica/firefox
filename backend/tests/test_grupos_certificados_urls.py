"""Tests for GruposCertificadosUrls API endpoints."""

import uuid

from backend.app.main import app
from backend.app.api.deps import check_auth_with_ip
from tests.factories.plano_factory import criar_plano
from tests.factories.grupo_factory import criar_grupo
from tests.factories.certificado_factory import criar_certificado
from tests.factories.grupo_certificado_factory import vincular_certificado_ao_grupo
from tests.factories.global_urls_factory import criar_global_url
from tests.factories.grupos_certificados_urls_factory import criar_grupos_certificados_urls
from tests.factories.grupo_usuario_factory import adicionar_usuario_ao_grupo


# ---------------------------------------------------------------------------
# Helper: mock check_auth
# ---------------------------------------------------------------------------
def _mock_user(user_id=None, org_id=None):
    """Return mock check_auth for authenticated user."""
    async def mock():
        return {
            "id": user_id or str(uuid.uuid4()),
            "is_admin": True,
            "organization_id": org_id or str(uuid.uuid4()),
            "email": "user@test.com",
        }
    return mock


# ---------------------------------------------------------------------------
# GET /grupos-certificados/{grupo_cert_id}/urls
# ---------------------------------------------------------------------------
def test_listar_urls_success(client, db_session):
    """List URLs for a grupo-certificado."""
    user_id = str(uuid.uuid4())
    empresa_id = str(uuid.uuid4())

    # Setup: plano -> grupo -> certificado -> grupo_cert -> global_url -> grupo_cert_url
    plano = criar_plano(db_session, empresa_id)
    grupo = criar_grupo(db_session, empresa_id, plano.plano_id)
    cert = criar_certificado(db_session, empresa_id, user_id)
    grupo_cert = vincular_certificado_ao_grupo(db_session, empresa_id, grupo.grupo_id, cert.certificado_id)
    global_url = criar_global_url(db_session, empresa_id, "https://api.example.com")
    criar_grupos_certificados_urls(db_session, grupo_cert.grupo_cert_id, global_url.global_urls_id, empresa_id)

    app.dependency_overrides[check_auth_with_ip] = _mock_user(user_id, empresa_id)

    response = client.get(f"/grupos-certificados/{grupo_cert.grupo_cert_id}/urls")

    app.dependency_overrides.pop(check_auth_with_ip, None)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["global_urls_id"] == str(global_url.global_urls_id)


def test_listar_urls_empty(client, db_session):
    """List returns empty when no URLs associated."""
    user_id = str(uuid.uuid4())
    empresa_id = str(uuid.uuid4())

    plano = criar_plano(db_session, empresa_id)
    grupo = criar_grupo(db_session, empresa_id, plano.plano_id)
    cert = criar_certificado(db_session, empresa_id, user_id)
    grupo_cert = vincular_certificado_ao_grupo(db_session, empresa_id, grupo.grupo_id, cert.certificado_id)

    app.dependency_overrides[check_auth_with_ip] = _mock_user(user_id, empresa_id)

    response = client.get(f"/grupos-certificados/{grupo_cert.grupo_cert_id}/urls")

    app.dependency_overrides.pop(check_auth_with_ip, None)

    assert response.status_code == 200
    assert response.json() == []


def test_listar_urls_unauthenticated(client):
    """Unauthenticated request gets 401."""
    fake_id = str(uuid.uuid4())

    response = client.get(f"/grupos-certificados/{fake_id}/urls")

    assert response.status_code == 401


# ---------------------------------------------------------------------------
# POST /grupos-certificados/{grupo_cert_id}/urls
# ---------------------------------------------------------------------------
def test_adicionar_url_success(client, db_session):
    """Add URL to grupo-certificado."""
    user_id = str(uuid.uuid4())
    empresa_id = str(uuid.uuid4())

    plano = criar_plano(db_session, empresa_id)
    grupo = criar_grupo(db_session, empresa_id, plano.plano_id)
    cert = criar_certificado(db_session, empresa_id, user_id)
    grupo_cert = vincular_certificado_ao_grupo(db_session, empresa_id, grupo.grupo_id, cert.certificado_id)
    global_url = criar_global_url(db_session, empresa_id, "https://api.example.com")

    app.dependency_overrides[check_auth_with_ip] = _mock_user(user_id, empresa_id)

    payload = {"global_urls_id": str(global_url.global_urls_id)}
    response = client.post(f"/grupos-certificados/{grupo_cert.grupo_cert_id}/urls", json=payload)

    app.dependency_overrides.pop(check_auth_with_ip, None)

    assert response.status_code == 201
    data = response.json()
    assert data["grupo_cert_id"] == str(grupo_cert.grupo_cert_id)
    assert data["global_urls_id"] == str(global_url.global_urls_id)


def test_adicionar_url_duplicate_returns_409(client, db_session):
    """Adding duplicate URL returns 409."""
    user_id = str(uuid.uuid4())
    empresa_id = str(uuid.uuid4())

    plano = criar_plano(db_session, empresa_id)
    grupo = criar_grupo(db_session, empresa_id, plano.plano_id)
    cert = criar_certificado(db_session, empresa_id, user_id)
    grupo_cert = vincular_certificado_ao_grupo(db_session, empresa_id, grupo.grupo_id, cert.certificado_id)
    global_url = criar_global_url(db_session, empresa_id, "https://api.example.com")

    # First association
    criar_grupos_certificados_urls(db_session, grupo_cert.grupo_cert_id, global_url.global_urls_id, empresa_id)

    app.dependency_overrides[check_auth_with_ip] = _mock_user(user_id, empresa_id)

    # Try to add same URL again
    payload = {"global_urls_id": str(global_url.global_urls_id)}
    response = client.post(f"/grupos-certificados/{grupo_cert.grupo_cert_id}/urls", json=payload)

    app.dependency_overrides.pop(check_auth_with_ip, None)

    assert response.status_code == 409


def test_adicionar_url_invalid_grupo_cert_returns_404(client, db_session):
    """Adding URL to nonexistent grupo-certificado returns 404."""
    user_id = str(uuid.uuid4())
    empresa_id = str(uuid.uuid4())

    global_url = criar_global_url(db_session, empresa_id, "https://api.example.com")
    fake_grupo_cert_id = str(uuid.uuid4())

    app.dependency_overrides[check_auth_with_ip] = _mock_user(user_id, empresa_id)

    payload = {"global_urls_id": str(global_url.global_urls_id)}
    response = client.post(f"/grupos-certificados/{fake_grupo_cert_id}/urls", json=payload)

    app.dependency_overrides.pop(check_auth_with_ip, None)

    assert response.status_code == 404


# ---------------------------------------------------------------------------
# DELETE /grupos-certificados-urls/{grupo_cert_url_id}
# ---------------------------------------------------------------------------
def test_remover_url_success(client, db_session):
    """Remove URL from grupo-certificado."""
    user_id = str(uuid.uuid4())
    empresa_id = str(uuid.uuid4())

    plano = criar_plano(db_session, empresa_id)
    grupo = criar_grupo(db_session, empresa_id, plano.plano_id)
    cert = criar_certificado(db_session, empresa_id, user_id)
    grupo_cert = vincular_certificado_ao_grupo(db_session, empresa_id, grupo.grupo_id, cert.certificado_id)
    global_url = criar_global_url(db_session, empresa_id, "https://api.example.com")
    grupo_cert_url = criar_grupos_certificados_urls(db_session, grupo_cert.grupo_cert_id, global_url.global_urls_id, empresa_id)

    app.dependency_overrides[check_auth_with_ip] = _mock_user(user_id, empresa_id)

    response = client.delete(f"/grupos-certificados-urls/{grupo_cert_url.grupo_cert_url_id}")

    app.dependency_overrides.pop(check_auth_with_ip, None)

    assert response.status_code == 200
    assert response.json()["status"] == "deleted"


def test_remover_url_nonexistent_returns_404(client, db_session):
    """Removing nonexistent URL returns 404."""
    user_id = str(uuid.uuid4())
    empresa_id = str(uuid.uuid4())
    fake_id = str(uuid.uuid4())

    app.dependency_overrides[check_auth_with_ip] = _mock_user(user_id, empresa_id)

    response = client.delete(f"/grupos-certificados-urls/{fake_id}")

    app.dependency_overrides.pop(check_auth_with_ip, None)

    assert response.status_code == 404


# ---------------------------------------------------------------------------
# Helper: mock check_auth for non-admin user
# ---------------------------------------------------------------------------
def _mock_non_admin_user(user_id=None, org_id=None):
    """Return mock check_auth for authenticated non-admin user."""
    async def mock():
        return {
            "id": user_id or str(uuid.uuid4()),
            "is_admin": False,
            "organization_id": org_id or str(uuid.uuid4()),
            "email": "user@test.com",
        }
    return mock


# ---------------------------------------------------------------------------
# GET /grupos-certificados/minhas-urls
# ---------------------------------------------------------------------------
def test_minhas_urls_success(client, db_session):
    """User gets their accessible URLs based on group membership."""
    user_id = str(uuid.uuid4())
    empresa_id = str(uuid.uuid4())

    # Setup: plano -> grupo -> certificado -> grupo_cert -> global_url -> grupo_cert_url
    plano = criar_plano(db_session, empresa_id)
    grupo = criar_grupo(db_session, empresa_id, plano.plano_id)
    cert = criar_certificado(db_session, empresa_id, user_id)
    grupo_cert = vincular_certificado_ao_grupo(db_session, empresa_id, grupo.grupo_id, cert.certificado_id)
    global_url = criar_global_url(db_session, empresa_id, "https://api.example.com")
    criar_grupos_certificados_urls(db_session, grupo_cert.grupo_cert_id, global_url.global_urls_id, empresa_id)

    # Add user to the grupo
    adicionar_usuario_ao_grupo(db_session, empresa_id, grupo.grupo_id, user_id)

    # Non-admin user should be able to access this endpoint
    app.dependency_overrides[check_auth_with_ip] = _mock_non_admin_user(user_id, empresa_id)

    response = client.get("/grupos-certificados/minhas-urls")

    app.dependency_overrides.pop(check_auth_with_ip, None)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["global_urls_id"] == str(global_url.global_urls_id)
    assert data[0]["url"] == "https://api.example.com"


def test_minhas_urls_returns_empty_when_user_not_in_grupo(client, db_session):
    """User gets empty list when not a member of any grupo."""
    user_id = str(uuid.uuid4())
    empresa_id = str(uuid.uuid4())

    # Setup data but don't add user to any grupo
    plano = criar_plano(db_session, empresa_id)
    grupo = criar_grupo(db_session, empresa_id, plano.plano_id)
    cert = criar_certificado(db_session, empresa_id, user_id)
    grupo_cert = vincular_certificado_ao_grupo(db_session, empresa_id, grupo.grupo_id, cert.certificado_id)
    global_url = criar_global_url(db_session, empresa_id, "https://api.example.com")
    criar_grupos_certificados_urls(db_session, grupo_cert.grupo_cert_id, global_url.global_urls_id, empresa_id)

    app.dependency_overrides[check_auth_with_ip] = _mock_non_admin_user(user_id, empresa_id)

    response = client.get("/grupos-certificados/minhas-urls")

    app.dependency_overrides.pop(check_auth_with_ip, None)

    assert response.status_code == 200
    assert response.json() == []


def test_minhas_urls_multiple_grupos(client, db_session):
    """User gets URLs from multiple grupos they belong to."""
    user_id = str(uuid.uuid4())
    empresa_id = str(uuid.uuid4())

    plano = criar_plano(db_session, empresa_id)

    # Setup first grupo with URL
    grupo1 = criar_grupo(db_session, empresa_id, plano.plano_id, nome="Grupo 1")
    cert1 = criar_certificado(db_session, empresa_id, user_id)
    grupo_cert1 = vincular_certificado_ao_grupo(db_session, empresa_id, grupo1.grupo_id, cert1.certificado_id)
    global_url1 = criar_global_url(db_session, empresa_id, "https://api1.example.com")
    criar_grupos_certificados_urls(db_session, grupo_cert1.grupo_cert_id, global_url1.global_urls_id, empresa_id)

    # Setup second grupo with URL
    grupo2 = criar_grupo(db_session, empresa_id, plano.plano_id, nome="Grupo 2")
    cert2 = criar_certificado(db_session, empresa_id, user_id)
    grupo_cert2 = vincular_certificado_ao_grupo(db_session, empresa_id, grupo2.grupo_id, cert2.certificado_id)
    global_url2 = criar_global_url(db_session, empresa_id, "https://api2.example.com")
    criar_grupos_certificados_urls(db_session, grupo_cert2.grupo_cert_id, global_url2.global_urls_id, empresa_id)

    # Add user to both grupos
    adicionar_usuario_ao_grupo(db_session, empresa_id, grupo1.grupo_id, user_id)
    adicionar_usuario_ao_grupo(db_session, empresa_id, grupo2.grupo_id, user_id)

    app.dependency_overrides[check_auth_with_ip] = _mock_non_admin_user(user_id, empresa_id)

    response = client.get("/grupos-certificados/minhas-urls")

    app.dependency_overrides.pop(check_auth_with_ip, None)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    urls = [item["url"] for item in data]
    assert "https://api1.example.com" in urls
    assert "https://api2.example.com" in urls


def test_minhas_urls_excludes_inactive_urls(client, db_session):
    """Inactive URLs are excluded from the results."""
    user_id = str(uuid.uuid4())
    empresa_id = str(uuid.uuid4())

    plano = criar_plano(db_session, empresa_id)
    grupo = criar_grupo(db_session, empresa_id, plano.plano_id)
    cert = criar_certificado(db_session, empresa_id, user_id)
    grupo_cert = vincular_certificado_ao_grupo(db_session, empresa_id, grupo.grupo_id, cert.certificado_id)

    # Create active URL
    active_url = criar_global_url(db_session, empresa_id, "https://active.example.com")
    criar_grupos_certificados_urls(db_session, grupo_cert.grupo_cert_id, active_url.global_urls_id, empresa_id)

    # Create inactive URL
    inactive_url = criar_global_url(db_session, empresa_id, "https://inactive.example.com")
    inactive_url.inativo = True
    db_session.commit()
    criar_grupos_certificados_urls(db_session, grupo_cert.grupo_cert_id, inactive_url.global_urls_id, empresa_id)

    adicionar_usuario_ao_grupo(db_session, empresa_id, grupo.grupo_id, user_id)

    app.dependency_overrides[check_auth_with_ip] = _mock_non_admin_user(user_id, empresa_id)

    response = client.get("/grupos-certificados/minhas-urls")

    app.dependency_overrides.pop(check_auth_with_ip, None)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["url"] == "https://active.example.com"


def test_minhas_urls_unauthenticated(client):
    """Unauthenticated request gets 401."""
    response = client.get("/grupos-certificados/minhas-urls")
    assert response.status_code == 401


def test_minhas_urls_no_organization(client, db_session):
    """User without organization gets 400."""
    user_id = str(uuid.uuid4())

    # Mock user without organization_id
    async def mock_no_org():
        return {
            "id": user_id,
            "is_admin": False,
            "organization_id": None,
            "email": "user@test.com",
        }

    app.dependency_overrides[check_auth_with_ip] = mock_no_org

    response = client.get("/grupos-certificados/minhas-urls")

    app.dependency_overrides.pop(check_auth_with_ip, None)

    assert response.status_code == 400
