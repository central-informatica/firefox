"""Tests for GruposCertificadosUrls API endpoints."""

import uuid

from backend.app.main import app
from backend.app.api.deps import check_auth
from tests.factories.plano_factory import criar_plano
from tests.factories.grupo_factory import criar_grupo
from tests.factories.certificado_factory import criar_certificado
from tests.factories.grupo_certificado_factory import vincular_certificado_ao_grupo
from tests.factories.global_urls_factory import criar_global_url
from tests.factories.grupos_certificados_urls_factory import criar_grupos_certificados_urls


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

    app.dependency_overrides[check_auth] = _mock_user(user_id, empresa_id)

    response = client.get(f"/grupos-certificados/{grupo_cert.grupo_cert_id}/urls")

    app.dependency_overrides.pop(check_auth, None)

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

    app.dependency_overrides[check_auth] = _mock_user(user_id, empresa_id)

    response = client.get(f"/grupos-certificados/{grupo_cert.grupo_cert_id}/urls")

    app.dependency_overrides.pop(check_auth, None)

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

    app.dependency_overrides[check_auth] = _mock_user(user_id, empresa_id)

    payload = {"global_urls_id": str(global_url.global_urls_id)}
    response = client.post(f"/grupos-certificados/{grupo_cert.grupo_cert_id}/urls", json=payload)

    app.dependency_overrides.pop(check_auth, None)

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

    app.dependency_overrides[check_auth] = _mock_user(user_id, empresa_id)

    # Try to add same URL again
    payload = {"global_urls_id": str(global_url.global_urls_id)}
    response = client.post(f"/grupos-certificados/{grupo_cert.grupo_cert_id}/urls", json=payload)

    app.dependency_overrides.pop(check_auth, None)

    assert response.status_code == 409


def test_adicionar_url_invalid_grupo_cert_returns_404(client, db_session):
    """Adding URL to nonexistent grupo-certificado returns 404."""
    user_id = str(uuid.uuid4())
    empresa_id = str(uuid.uuid4())

    global_url = criar_global_url(db_session, empresa_id, "https://api.example.com")
    fake_grupo_cert_id = str(uuid.uuid4())

    app.dependency_overrides[check_auth] = _mock_user(user_id, empresa_id)

    payload = {"global_urls_id": str(global_url.global_urls_id)}
    response = client.post(f"/grupos-certificados/{fake_grupo_cert_id}/urls", json=payload)

    app.dependency_overrides.pop(check_auth, None)

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

    app.dependency_overrides[check_auth] = _mock_user(user_id, empresa_id)

    response = client.delete(f"/grupos-certificados-urls/{grupo_cert_url.grupo_cert_url_id}")

    app.dependency_overrides.pop(check_auth, None)

    assert response.status_code == 200
    assert response.json()["status"] == "deleted"


def test_remover_url_nonexistent_returns_404(client, db_session):
    """Removing nonexistent URL returns 404."""
    user_id = str(uuid.uuid4())
    empresa_id = str(uuid.uuid4())
    fake_id = str(uuid.uuid4())

    app.dependency_overrides[check_auth] = _mock_user(user_id, empresa_id)

    response = client.delete(f"/grupos-certificados-urls/{fake_id}")

    app.dependency_overrides.pop(check_auth, None)

    assert response.status_code == 404
