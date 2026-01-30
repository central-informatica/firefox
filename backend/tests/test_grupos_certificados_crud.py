"""Functional tests for GruposCertificados CRUD API endpoints."""

import uuid

from backend.app.main import app
from backend.app.api.deps import check_auth_with_ip
from backend.app.db.models import GruposCertificados
from tests.factories.grupo_factory import criar_grupo
from tests.factories.certificado_factory import criar_certificado
from tests.factories.grupo_certificado_factory import vincular_certificado_ao_grupo
from tests.factories.plano_factory import criar_plano


# ---------------------------------------------------------------------------
# Helper: mock check_auth_with_ip
# ---------------------------------------------------------------------------
def _mock_admin(user_id=None, org_id=None, ip="127.0.0.1"):
    """Return mock check_auth_with_ip for admin user."""
    async def mock():
        return {
            "id": user_id or str(uuid.uuid4()),
            "is_admin": True,
            "organization_id": org_id or str(uuid.uuid4()),
            "email": "admin@test.com",
            "ip_address": ip,
        }
    return mock


# ---------------------------------------------------------------------------
# GET /grupos-certificados/ - List All
# ---------------------------------------------------------------------------
def test_listar_grupos_certificados_success(client, db_session):
    """Admin can list all grupo-certificado relationships."""
    user_id = str(uuid.uuid4())
    empresa_id = str(uuid.uuid4())

    # Create test data
    plano = criar_plano(db_session, empresa_id, nome="Plano Teste")
    grupo = criar_grupo(db_session, empresa_id, plano.plano_id, nome="Grupo Teste")
    cert = criar_certificado(db_session, empresa_id, user_id, nome_arquivo="teste.pfx")

    vincular_certificado_ao_grupo(db_session, empresa_id, grupo.grupo_id, cert.certificado_id)

    app.dependency_overrides[check_auth_with_ip] = _mock_admin(user_id, empresa_id)

    response = client.get("/grupos-certificados/")

    app.dependency_overrides.pop(check_auth_with_ip, None)

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_listar_grupos_certificados_empty(client, db_session):
    """Listing grupos-certificados returns empty array when none exist."""
    user_id = str(uuid.uuid4())
    empresa_id = str(uuid.uuid4())

    app.dependency_overrides[check_auth_with_ip] = _mock_admin(user_id, empresa_id)

    response = client.get("/grupos-certificados/")

    app.dependency_overrides.pop(check_auth_with_ip, None)

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0


def test_listar_grupos_certificados_unauthenticated(client):
    """Unauthenticated request returns 401."""
    response = client.get("/grupos-certificados/")
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# GET /grupos-certificados/grupo/{grupo_id} - List by Grupo
# ---------------------------------------------------------------------------
def test_listar_por_grupo_success(client, db_session):
    """Admin can list grupo-certificados for a specific grupo."""
    user_id = str(uuid.uuid4())
    empresa_id = str(uuid.uuid4())

    # Create test data
    plano = criar_plano(db_session, empresa_id, nome="Plano Teste")
    grupo = criar_grupo(db_session, empresa_id, plano.plano_id, nome="Grupo Teste")
    cert = criar_certificado(db_session, empresa_id, user_id, nome_arquivo="teste.pfx")

    vincular_certificado_ao_grupo(db_session, empresa_id, grupo.grupo_id, cert.certificado_id)

    app.dependency_overrides[check_auth_with_ip] = _mock_admin(user_id, empresa_id)

    response = client.get(f"/grupos-certificados/grupo/{grupo.grupo_id}")

    app.dependency_overrides.pop(check_auth_with_ip, None)

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["grupo_id"] == str(grupo.grupo_id)


def test_listar_por_grupo_empty(client, db_session):
    """Listing certificados for grupo with no certs returns empty array."""
    user_id = str(uuid.uuid4())
    empresa_id = str(uuid.uuid4())

    # Create grupo without certificados
    plano = criar_plano(db_session, empresa_id, nome="Plano Teste")
    grupo = criar_grupo(db_session, empresa_id, plano.plano_id, nome="Grupo Vazio")

    app.dependency_overrides[check_auth_with_ip] = _mock_admin(user_id, empresa_id)

    response = client.get(f"/grupos-certificados/grupo/{grupo.grupo_id}")

    app.dependency_overrides.pop(check_auth_with_ip, None)

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0


def test_listar_por_grupo_multiple_certificados(client, db_session):
    """Listing grupo with multiple certificados returns all."""
    user_id = str(uuid.uuid4())
    empresa_id = str(uuid.uuid4())

    # Create test data
    plano = criar_plano(db_session, empresa_id, nome="Plano Teste")
    grupo = criar_grupo(db_session, empresa_id, plano.plano_id, nome="Grupo Multi")
    cert1 = criar_certificado(db_session, empresa_id, user_id, nome_arquivo="cert1.pfx")
    cert2 = criar_certificado(db_session, empresa_id, user_id, nome_arquivo="cert2.pfx")

    vincular_certificado_ao_grupo(db_session, empresa_id, grupo.grupo_id, cert1.certificado_id)
    vincular_certificado_ao_grupo(db_session, empresa_id, grupo.grupo_id, cert2.certificado_id)

    app.dependency_overrides[check_auth_with_ip] = _mock_admin(user_id, empresa_id)

    response = client.get(f"/grupos-certificados/grupo/{grupo.grupo_id}")

    app.dependency_overrides.pop(check_auth_with_ip, None)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_listar_por_grupo_unauthenticated(client):
    """Unauthenticated request returns 401."""
    fake_grupo_id = str(uuid.uuid4())
    response = client.get(f"/grupos-certificados/grupo/{fake_grupo_id}")
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# GET /grupos-certificados/{grupo_cert_id} - Get One
# ---------------------------------------------------------------------------
def test_obter_grupo_certificado_success(client, db_session):
    """Admin can get a specific grupo-certificado relationship."""
    user_id = str(uuid.uuid4())
    empresa_id = str(uuid.uuid4())

    # Create test data
    plano = criar_plano(db_session, empresa_id, nome="Plano Teste")
    grupo = criar_grupo(db_session, empresa_id, plano.plano_id, nome="Grupo Teste")
    cert = criar_certificado(db_session, empresa_id, user_id, nome_arquivo="teste.pfx")

    gc = vincular_certificado_ao_grupo(db_session, empresa_id, grupo.grupo_id, cert.certificado_id)

    app.dependency_overrides[check_auth_with_ip] = _mock_admin(user_id, empresa_id)

    response = client.get(f"/grupos-certificados/{gc.grupo_cert_id}")

    app.dependency_overrides.pop(check_auth_with_ip, None)

    assert response.status_code == 200
    data = response.json()
    assert data["grupo_cert_id"] == str(gc.grupo_cert_id)
    assert data["grupo_id"] == str(grupo.grupo_id)
    assert data["certificado_id"] == str(cert.certificado_id)


def test_obter_grupo_certificado_not_found(client, db_session):
    """Getting nonexistent grupo-certificado returns 404."""
    user_id = str(uuid.uuid4())
    empresa_id = str(uuid.uuid4())
    fake_id = str(uuid.uuid4())

    app.dependency_overrides[check_auth_with_ip] = _mock_admin(user_id, empresa_id)

    response = client.get(f"/grupos-certificados/{fake_id}")

    app.dependency_overrides.pop(check_auth_with_ip, None)

    assert response.status_code == 404
    assert "não encontrada" in response.json()["detail"].lower()


def test_obter_grupo_certificado_unauthenticated(client):
    """Unauthenticated request returns 401."""
    fake_id = str(uuid.uuid4())
    response = client.get(f"/grupos-certificados/{fake_id}")
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# POST /grupos-certificados/ - Create
# ---------------------------------------------------------------------------
def test_criar_grupo_certificado_success(client, db_session):
    """Admin can create a grupo-certificado relationship."""
    user_id = str(uuid.uuid4())
    empresa_id = str(uuid.uuid4())

    # Create dependencies
    plano = criar_plano(db_session, empresa_id, nome="Plano Teste")
    grupo = criar_grupo(db_session, empresa_id, plano.plano_id, nome="Grupo Teste")
    cert = criar_certificado(db_session, empresa_id, user_id, nome_arquivo="teste.pfx")

    app.dependency_overrides[check_auth_with_ip] = _mock_admin(user_id, empresa_id)

    payload = {
        "grupo_id": str(grupo.grupo_id),
        "certificado_id": str(cert.certificado_id),
        "empresa_id": empresa_id,
    }
    response = client.post("/grupos-certificados/", json=payload)

    app.dependency_overrides.pop(check_auth_with_ip, None)

    assert response.status_code == 201
    data = response.json()
    assert data["grupo_id"] == str(grupo.grupo_id)
    assert data["certificado_id"] == str(cert.certificado_id)
    assert "grupo_cert_id" in data


def test_criar_grupo_certificado_missing_required_fields(client, db_session):
    """Creating without required fields returns 422."""
    user_id = str(uuid.uuid4())
    empresa_id = str(uuid.uuid4())

    app.dependency_overrides[check_auth_with_ip] = _mock_admin(user_id, empresa_id)

    payload = {"grupo_id": str(uuid.uuid4())}  # Missing certificado_id and empresa_id
    response = client.post("/grupos-certificados/", json=payload)

    app.dependency_overrides.pop(check_auth_with_ip, None)

    assert response.status_code == 422


def test_criar_grupo_certificado_unauthenticated(client):
    """Unauthenticated request returns 401."""
    payload = {
        "grupo_id": str(uuid.uuid4()),
        "certificado_id": str(uuid.uuid4()),
        "empresa_id": str(uuid.uuid4()),
    }
    response = client.post("/grupos-certificados/", json=payload)
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# PUT /grupos-certificados/{grupo_cert_id} - Update
# ---------------------------------------------------------------------------
def test_atualizar_grupo_certificado_success(client, db_session):
    """Admin can update a grupo-certificado relationship."""
    user_id = str(uuid.uuid4())
    empresa_id = str(uuid.uuid4())

    # Create test data
    plano = criar_plano(db_session, empresa_id, nome="Plano Teste")
    grupo1 = criar_grupo(db_session, empresa_id, plano.plano_id, nome="Grupo 1")
    grupo2 = criar_grupo(db_session, empresa_id, plano.plano_id, nome="Grupo 2")
    cert = criar_certificado(db_session, empresa_id, user_id, nome_arquivo="teste.pfx")

    gc = vincular_certificado_ao_grupo(db_session, empresa_id, grupo1.grupo_id, cert.certificado_id)

    app.dependency_overrides[check_auth_with_ip] = _mock_admin(user_id, empresa_id)

    payload = {"grupo_id": str(grupo2.grupo_id)}  # Change to grupo2
    response = client.put(f"/grupos-certificados/{gc.grupo_cert_id}", json=payload)

    app.dependency_overrides.pop(check_auth_with_ip, None)

    assert response.status_code == 200
    data = response.json()
    assert data["grupo_id"] == str(grupo2.grupo_id)


def test_atualizar_grupo_certificado_not_found(client, db_session):
    """Updating nonexistent grupo-certificado returns 404."""
    user_id = str(uuid.uuid4())
    empresa_id = str(uuid.uuid4())
    fake_id = str(uuid.uuid4())

    app.dependency_overrides[check_auth_with_ip] = _mock_admin(user_id, empresa_id)

    payload = {"grupo_id": str(uuid.uuid4())}
    response = client.put(f"/grupos-certificados/{fake_id}", json=payload)

    app.dependency_overrides.pop(check_auth_with_ip, None)

    assert response.status_code == 404
    assert "não encontrada" in response.json()["detail"].lower()


def test_atualizar_grupo_certificado_unauthenticated(client):
    """Unauthenticated request returns 401."""
    fake_id = str(uuid.uuid4())
    payload = {"grupo_id": str(uuid.uuid4())}
    response = client.put(f"/grupos-certificados/{fake_id}", json=payload)
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# DELETE /grupos-certificados/{grupo_cert_id} - Delete
# ---------------------------------------------------------------------------
def test_deletar_grupo_certificado_success(client, db_session):
    """Admin can delete a grupo-certificado relationship."""
    user_id = str(uuid.uuid4())
    empresa_id = str(uuid.uuid4())

    # Create test data
    plano = criar_plano(db_session, empresa_id, nome="Plano Teste")
    grupo = criar_grupo(db_session, empresa_id, plano.plano_id, nome="Grupo Teste")
    cert = criar_certificado(db_session, empresa_id, user_id, nome_arquivo="teste.pfx")

    gc = vincular_certificado_ao_grupo(db_session, empresa_id, grupo.grupo_id, cert.certificado_id)

    # Verify exists before delete
    assert db_session.query(GruposCertificados).filter(
        GruposCertificados.grupo_cert_id == gc.grupo_cert_id
    ).count() == 1

    app.dependency_overrides[check_auth_with_ip] = _mock_admin(user_id, empresa_id)

    response = client.delete(f"/grupos-certificados/{gc.grupo_cert_id}")

    app.dependency_overrides.pop(check_auth_with_ip, None)

    assert response.status_code == 200
    assert response.json()["status"] == "deleted"

    # Verify deleted
    assert db_session.query(GruposCertificados).filter(
        GruposCertificados.grupo_cert_id == gc.grupo_cert_id
    ).count() == 0


def test_deletar_grupo_certificado_not_found(client, db_session):
    """Deleting nonexistent grupo-certificado returns 404."""
    user_id = str(uuid.uuid4())
    empresa_id = str(uuid.uuid4())
    fake_id = str(uuid.uuid4())

    app.dependency_overrides[check_auth_with_ip] = _mock_admin(user_id, empresa_id)

    response = client.delete(f"/grupos-certificados/{fake_id}")

    app.dependency_overrides.pop(check_auth_with_ip, None)

    assert response.status_code == 404
    assert "não encontrada" in response.json()["detail"].lower()


def test_deletar_grupo_certificado_unauthenticated(client):
    """Unauthenticated request returns 401."""
    fake_id = str(uuid.uuid4())
    response = client.delete(f"/grupos-certificados/{fake_id}")
    assert response.status_code == 401
