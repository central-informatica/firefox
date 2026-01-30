import uuid
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.api.deps import check_auth_with_ip
from backend.app.db.session import get_db

from tests.factories.plano_factory import criar_plano
from tests.factories.grupo_factory import criar_grupo
from tests.factories.usuarios_ip_whitelist_factory import criar_usuarios_ip_whitelist
from tests.factories.certificado_factory import criar_certificado
from tests.factories.grupo_certificado_factory import vincular_certificado_ao_grupo
from tests.factories.grupo_usuario_factory import adicionar_usuario_ao_grupo
from backend.app.db.models import GruposCertificados, GruposUsuarios
from backend.app.crud.grupos import get_grupo


def _mock_user_data(user_id: str, org_id: str, is_admin: bool = True, ip: str = "127.0.0.1"):
    """Create mock user data dict as returned by auth service."""
    return {
        "id": user_id,
        "usuario_id": user_id,
        "organization_id": org_id,
        "is_admin": is_admin,
        "email": "admin@test.com",
        "ip_address": ip,
    }


@pytest.fixture
def admin_client(db_session):
    """Test client with admin user and whitelisted IP."""
    user_id = str(uuid.uuid4())
    empresa_id = str(uuid.uuid4())

    criar_usuarios_ip_whitelist(
        db_session,
        usuario_id=user_id,
        empresa_id=empresa_id,
        ip_address="127.0.0.1",
    )

    async def mock_auth():
        return _mock_user_data(user_id, empresa_id, is_admin=True, ip="127.0.0.1")

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[check_auth_with_ip] = mock_auth
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client, user_id, empresa_id

    app.dependency_overrides.clear()

def test_criar_grupo(admin_client):
    client, user_id, empresa_id = admin_client

    plano = criar_plano(client._transport.app.dependency_overrides[get_db]().__next__(), empresa_id)

    payload = {
        "empresa_id": empresa_id,
        "plano_id": str(plano.plano_id),
        "nome": "Grupo Financeiro",
    }

    response = client.post("/grupos", json=payload)

    assert response.status_code == 201
    assert response.json()["nome"] == "Grupo Financeiro"


def test_grupo_nome_duplicado_na_empresa(admin_client, db_session):
    client, user_id, empresa_id = admin_client

    plano = criar_plano(db_session, empresa_id)
    criar_grupo(db_session, empresa_id, plano.plano_id, nome="Duplicado")

    payload = {
        "empresa_id": empresa_id,
        "plano_id": str(plano.plano_id),
        "nome": "Duplicado",
    }

    response = client.post("/grupos", json=payload)

    assert response.status_code == 400


def test_listar_grupos_por_plano(admin_client, db_session):
    client, user_id, empresa_id = admin_client

    plano = criar_plano(db_session, empresa_id)

    criar_grupo(db_session, empresa_id, plano.plano_id, nome="Grupo A")
    criar_grupo(db_session, empresa_id, plano.plano_id, nome="Grupo B")

    response = client.get(f"/grupos?plano_id={plano.plano_id}")

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_buscar_grupo_por_id(admin_client, db_session):
    client, user_id, empresa_id = admin_client

    plano = criar_plano(db_session, empresa_id)
    grupo = criar_grupo(db_session, empresa_id, plano.plano_id)

    response = client.get(f"/grupos/{grupo.grupo_id}")

    assert response.status_code == 200
    assert str(response.json()["grupo_id"]) == str(grupo.grupo_id)


def test_editar_grupo(admin_client, db_session):
    client, user_id, empresa_id = admin_client

    plano = criar_plano(db_session, empresa_id)
    grupo = criar_grupo(db_session, empresa_id, plano.plano_id)

    payload = {"nome": "Grupo Atualizado"}

    response = client.put(f"/grupos/{grupo.grupo_id}", json=payload)

    assert response.status_code == 200
    assert response.json()["nome"] == "Grupo Atualizado"


def test_grupo_nao_acessivel_por_outro_usuario(db_session):
    """Test that a user from different empresa cannot access grupo."""
    # Create empresa A with a grupo
    empresa_a_id = str(uuid.uuid4())
    user_a_id = str(uuid.uuid4())

    plano = criar_plano(db_session, empresa_a_id)
    grupo = criar_grupo(db_session, empresa_a_id, plano.plano_id)

    # Create user B from empresa B
    user_b_id = str(uuid.uuid4())
    empresa_b_id = str(uuid.uuid4())

    criar_usuarios_ip_whitelist(
        db_session,
        usuario_id=user_b_id,
        empresa_id=empresa_b_id,
        ip_address="127.0.0.1",
    )

    async def mock_auth_user_b():
        return _mock_user_data(user_b_id, empresa_b_id, is_admin=True, ip="127.0.0.1")

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[check_auth_with_ip] = mock_auth_user_b
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as client_b:
        response = client_b.get(f"/grupos/{grupo.grupo_id}")
        # Should be forbidden or not found since user B is from different empresa
        assert response.status_code in (403, 404)

    app.dependency_overrides.clear()


def test_listar_grupos_sem_login():
    """Test that unauthenticated requests are rejected."""
    with TestClient(app) as client:
        response = client.get("/grupos")
        assert response.status_code == 401


def test_listar_grupos_por_empresa(admin_client, db_session):
    """Test listing grupos by empresa successfully."""
    client, user_id, empresa_id = admin_client

    plano = criar_plano(db_session, empresa_id)

    criar_grupo(db_session, empresa_id, plano.plano_id, nome="Grupo A")
    criar_grupo(db_session, empresa_id, plano.plano_id, nome="Grupo B")
    criar_grupo(db_session, empresa_id, plano.plano_id, nome="Grupo C")

    response = client.get(f"/grupos/empresa/{empresa_id}")

    assert response.status_code == 200
    assert len(response.json()) == 3
    grupo_names = [g["nome"] for g in response.json()]
    assert "Grupo A" in grupo_names
    assert "Grupo B" in grupo_names
    assert "Grupo C" in grupo_names


def test_listar_grupos_por_empresa_filtrado_por_plano(admin_client, db_session):
    """Test listing grupos by empresa filtered by plano_id."""
    client, user_id, empresa_id = admin_client

    plano1 = criar_plano(db_session, empresa_id, nome="Plano 1")
    plano2 = criar_plano(db_session, empresa_id, nome="Plano 2")

    criar_grupo(db_session, empresa_id, plano1.plano_id, nome="Grupo Plano 1A")
    criar_grupo(db_session, empresa_id, plano1.plano_id, nome="Grupo Plano 1B")
    criar_grupo(db_session, empresa_id, plano2.plano_id, nome="Grupo Plano 2A")

    response = client.get(f"/grupos/empresa/{empresa_id}?plano_id={plano1.plano_id}")

    assert response.status_code == 200
    assert len(response.json()) == 2
    grupo_names = [g["nome"] for g in response.json()]
    assert "Grupo Plano 1A" in grupo_names
    assert "Grupo Plano 1B" in grupo_names
    assert "Grupo Plano 2A" not in grupo_names


def test_listar_grupos_empresa_vazia(admin_client, db_session):
    """Test listing grupos for an empresa with no grupos."""
    client, user_id, empresa_id = admin_client

    response = client.get(f"/grupos/empresa/{empresa_id}")

    assert response.status_code == 200
    assert response.json() == []


def test_listar_grupos_de_outra_empresa_proibido(db_session):
    """Test that non-admin user cannot list grupos from another empresa."""
    # Empresa A with grupos
    empresa_a_id = str(uuid.uuid4())
    plano_a = criar_plano(db_session, empresa_a_id)
    criar_grupo(db_session, empresa_a_id, plano_a.plano_id, nome="Grupo A")

    # Non-admin user B from empresa B
    user_b_id = str(uuid.uuid4())
    empresa_b_id = str(uuid.uuid4())

    criar_usuarios_ip_whitelist(
        db_session,
        usuario_id=user_b_id,
        empresa_id=empresa_b_id,
        ip_address="127.0.0.1",
    )

    async def mock_auth_user_b():
        return _mock_user_data(user_b_id, empresa_b_id, is_admin=False, ip="127.0.0.1")

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[check_auth_with_ip] = mock_auth_user_b
    app.dependency_overrides[get_db] = override_get_db

    # Try to list grupos from empresa A
    with TestClient(app) as client_b:
        response = client_b.get(f"/grupos/empresa/{empresa_a_id}")

        # Should be forbidden (403) since user B is not admin and not member of empresa A
        assert response.status_code == 403

    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Phase 1: Grupo Deletion Tests
# ---------------------------------------------------------------------------

def test_deletar_grupo(admin_client, db_session):
    """Test successful deletion of a grupo."""
    client, user_id, empresa_id = admin_client

    plano = criar_plano(db_session, empresa_id)
    grupo = criar_grupo(db_session, empresa_id, plano.plano_id, nome="Grupo Para Deletar")

    response = client.delete(f"/grupos/{grupo.grupo_id}")

    assert response.status_code == 200
    assert response.json()["detail"] == "Grupo removido com sucesso"

    # Verify grupo is deleted from database
    grupo_deleted = get_grupo(db_session, str(grupo.grupo_id))
    assert grupo_deleted is None


def test_deletar_grupo_nao_existente(admin_client):
    """Test deleting non-existent grupo returns 404."""
    client, user_id, empresa_id = admin_client

    fake_id = str(uuid.uuid4())
    response = client.delete(f"/grupos/{fake_id}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Grupo nao encontrado"


# ---------------------------------------------------------------------------
# Phase 2: Certificado Management Tests
# ---------------------------------------------------------------------------

def test_listar_certificados_do_grupo_vazio(admin_client, db_session):
    """Test listing certificados from empty grupo."""
    client, user_id, empresa_id = admin_client

    plano = criar_plano(db_session, empresa_id)
    grupo = criar_grupo(db_session, empresa_id, plano.plano_id)

    response = client.get(f"/grupos/{grupo.grupo_id}/certificados")

    assert response.status_code == 200
    assert response.json() == []


def test_listar_certificados_do_grupo(admin_client, db_session):
    """Test listing certificados in a grupo."""
    client, user_id, empresa_id = admin_client

    plano = criar_plano(db_session, empresa_id)
    grupo = criar_grupo(db_session, empresa_id, plano.plano_id)
    cert1 = criar_certificado(db_session, empresa_id, user_id, nome_arquivo="cert1.pfx")
    cert2 = criar_certificado(db_session, empresa_id, user_id, nome_arquivo="cert2.pfx")

    vincular_certificado_ao_grupo(db_session, empresa_id, grupo.grupo_id, cert1.certificado_id)
    vincular_certificado_ao_grupo(db_session, empresa_id, grupo.grupo_id, cert2.certificado_id)

    response = client.get(f"/grupos/{grupo.grupo_id}/certificados")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2

    cert_ids = [str(c["certificado_id"]) for c in data]
    assert str(cert1.certificado_id) in cert_ids
    assert str(cert2.certificado_id) in cert_ids

    cert_names = [c["nome_arquivo"] for c in data]
    assert "cert1.pfx" in cert_names
    assert "cert2.pfx" in cert_names


def test_adicionar_certificado_ao_grupo(admin_client, db_session):
    """Test adding certificado to grupo."""
    client, user_id, empresa_id = admin_client

    plano = criar_plano(db_session, empresa_id)
    grupo = criar_grupo(db_session, empresa_id, plano.plano_id)
    cert = criar_certificado(db_session, empresa_id, user_id, nome_arquivo="test.pfx")

    payload = {
        "empresa_id": empresa_id,
        "certificado_id": str(cert.certificado_id)
    }

    response = client.post(f"/grupos/{grupo.grupo_id}/certificados", json=payload)

    assert response.status_code == 201
    assert "grupo_cert_id" in response.json()

    # Verify link exists in database
    link = db_session.query(GruposCertificados).filter(
        GruposCertificados.grupo_id == grupo.grupo_id,
        GruposCertificados.certificado_id == cert.certificado_id
    ).first()
    assert link is not None


def test_adicionar_certificado_duplicado_ao_grupo(admin_client, db_session):
    """Test adding same certificado twice (idempotent behavior)."""
    client, user_id, empresa_id = admin_client

    plano = criar_plano(db_session, empresa_id)
    grupo = criar_grupo(db_session, empresa_id, plano.plano_id)
    cert = criar_certificado(db_session, empresa_id, user_id, nome_arquivo="test.pfx")

    # Add certificado first time
    vincular_certificado_ao_grupo(db_session, empresa_id, grupo.grupo_id, cert.certificado_id)

    # Try to add again
    payload = {
        "empresa_id": empresa_id,
        "certificado_id": str(cert.certificado_id)
    }

    response = client.post(f"/grupos/{grupo.grupo_id}/certificados", json=payload)

    assert response.status_code == 201  # Idempotent - returns existing

    # Verify only one link exists
    link_count = db_session.query(GruposCertificados).filter(
        GruposCertificados.grupo_id == grupo.grupo_id,
        GruposCertificados.certificado_id == cert.certificado_id
    ).count()
    assert link_count == 1


def test_adicionar_certificado_de_outra_empresa_ao_grupo(admin_client, db_session):
    """Test multi-tenant isolation: cannot add certificado from different empresa."""
    client, user_id, empresa_id = admin_client

    plano = criar_plano(db_session, empresa_id)
    grupo = criar_grupo(db_session, empresa_id, plano.plano_id)

    # Create certificado from different empresa
    outra_empresa_id = str(uuid.uuid4())
    outro_user_id = str(uuid.uuid4())
    cert = criar_certificado(db_session, outra_empresa_id, outro_user_id, nome_arquivo="test.pfx")

    payload = {
        "empresa_id": empresa_id,
        "certificado_id": str(cert.certificado_id)
    }

    response = client.post(f"/grupos/{grupo.grupo_id}/certificados", json=payload)

    assert response.status_code == 403
    assert "Certificado não pertence à empresa" in response.json()["detail"]


def test_remover_certificado_do_grupo(admin_client, db_session):
    """Test removing certificado from grupo."""
    client, user_id, empresa_id = admin_client

    plano = criar_plano(db_session, empresa_id)
    grupo = criar_grupo(db_session, empresa_id, plano.plano_id)
    cert = criar_certificado(db_session, empresa_id, user_id, nome_arquivo="test.pfx")

    # Add certificado to grupo
    vincular_certificado_ao_grupo(db_session, empresa_id, grupo.grupo_id, cert.certificado_id)

    payload = {
        "empresa_id": empresa_id,
        "certificado_id": str(cert.certificado_id)
    }

    response = client.request("DELETE", f"/grupos/{grupo.grupo_id}/certificados", json=payload)

    assert response.status_code == 200
    assert response.json()["success"] == True

    # Verify link no longer exists in database
    link = db_session.query(GruposCertificados).filter(
        GruposCertificados.grupo_id == grupo.grupo_id,
        GruposCertificados.certificado_id == cert.certificado_id
    ).first()
    assert link is None


def test_remover_certificado_inexistente_do_grupo(admin_client, db_session):
    """Test removing non-existent certificado-grupo link returns 404."""
    client, user_id, empresa_id = admin_client

    plano = criar_plano(db_session, empresa_id)
    grupo = criar_grupo(db_session, empresa_id, plano.plano_id)
    cert = criar_certificado(db_session, empresa_id, user_id, nome_arquivo="test.pfx")

    # Note: Not linking certificado to grupo

    payload = {
        "empresa_id": empresa_id,
        "certificado_id": str(cert.certificado_id)
    }

    response = client.request("DELETE", f"/grupos/{grupo.grupo_id}/certificados", json=payload)

    assert response.status_code == 404
    assert response.json()["detail"] == "Vinculo nao encontrado"


# ---------------------------------------------------------------------------
# Phase 3: Usuario Management Tests
# ---------------------------------------------------------------------------

def test_listar_usuarios_do_grupo_vazio(admin_client, db_session):
    """Test listing usuarios from empty grupo."""
    client, user_id, empresa_id = admin_client

    plano = criar_plano(db_session, empresa_id)
    grupo = criar_grupo(db_session, empresa_id, plano.plano_id)

    response = client.get(f"/grupos/{grupo.grupo_id}/usuarios")

    assert response.status_code == 200
    assert response.json() == []


def test_listar_usuarios_do_grupo(admin_client, db_session):
    """Test listing usuarios in a grupo."""
    client, user_id, empresa_id = admin_client

    plano = criar_plano(db_session, empresa_id)
    grupo = criar_grupo(db_session, empresa_id, plano.plano_id)

    user1_id = str(uuid.uuid4())
    user2_id = str(uuid.uuid4())

    adicionar_usuario_ao_grupo(db_session, empresa_id, grupo.grupo_id, user1_id)
    adicionar_usuario_ao_grupo(db_session, empresa_id, grupo.grupo_id, user2_id)

    response = client.get(f"/grupos/{grupo.grupo_id}/usuarios")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2

    usuario_ids = [u["usuario_id"] for u in data]
    assert user1_id in usuario_ids
    assert user2_id in usuario_ids


def test_adicionar_usuario_ao_grupo(admin_client, db_session):
    """Test adding usuario to grupo."""
    client, user_id, empresa_id = admin_client

    plano = criar_plano(db_session, empresa_id)
    grupo = criar_grupo(db_session, empresa_id, plano.plano_id)
    novo_usuario_id = str(uuid.uuid4())

    payload = {
        "empresa_id": empresa_id,
        "usuario_id": novo_usuario_id
    }

    response = client.post(f"/grupos/{grupo.grupo_id}/usuarios", json=payload)

    assert response.status_code == 201
    assert "grupo_usuario_id" in response.json()

    # Verify link exists in database
    link = db_session.query(GruposUsuarios).filter(
        GruposUsuarios.grupo_id == grupo.grupo_id,
        GruposUsuarios.usuario_id == novo_usuario_id
    ).first()
    assert link is not None
    assert str(link.grupo_id) == str(grupo.grupo_id)
    assert str(link.usuario_id) == novo_usuario_id


def test_adicionar_usuario_a_grupo_inexistente(admin_client):
    """Test adding usuario to non-existent grupo returns 404."""
    client, user_id, empresa_id = admin_client

    fake_grupo_id = str(uuid.uuid4())
    novo_usuario_id = str(uuid.uuid4())

    payload = {
        "empresa_id": empresa_id,
        "usuario_id": novo_usuario_id
    }

    response = client.post(f"/grupos/{fake_grupo_id}/usuarios", json=payload)

    assert response.status_code == 404
    assert response.json()["detail"] == "Grupo nao encontrado"


def test_remover_usuario_do_grupo(admin_client, db_session):
    """Test removing usuario from grupo."""
    client, user_id, empresa_id = admin_client

    plano = criar_plano(db_session, empresa_id)
    grupo = criar_grupo(db_session, empresa_id, plano.plano_id)
    usuario_id = str(uuid.uuid4())

    # Add usuario to grupo
    adicionar_usuario_ao_grupo(db_session, empresa_id, grupo.grupo_id, usuario_id)

    response = client.delete(f"/grupos/{grupo.grupo_id}/usuarios/{usuario_id}")

    assert response.status_code == 200
    assert response.json()["status"] == "deleted"

    # Verify link no longer exists in database
    link = db_session.query(GruposUsuarios).filter(
        GruposUsuarios.grupo_id == grupo.grupo_id,
        GruposUsuarios.usuario_id == usuario_id
    ).first()
    assert link is None


def test_remover_usuario_inexistente_do_grupo(admin_client, db_session):
    """Test removing non-existent usuario-grupo link returns 404."""
    client, user_id, empresa_id = admin_client

    plano = criar_plano(db_session, empresa_id)
    grupo = criar_grupo(db_session, empresa_id, plano.plano_id)
    usuario_id = str(uuid.uuid4())

    # Note: Not adding usuario to grupo

    response = client.delete(f"/grupos/{grupo.grupo_id}/usuarios/{usuario_id}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Vinculo nao encontrado"


def test_adicionar_usuarios_em_lote(admin_client, db_session):
    """Test bulk adding usuarios to grupo."""
    client, user_id, empresa_id = admin_client

    plano = criar_plano(db_session, empresa_id)
    grupo = criar_grupo(db_session, empresa_id, plano.plano_id)

    user1_id = str(uuid.uuid4())
    user2_id = str(uuid.uuid4())
    user3_id = str(uuid.uuid4())

    payload = {
        "grupo_id": str(grupo.grupo_id),
        "empresa_id": empresa_id,
        "usuario_ids": [user1_id, user2_id, user3_id]
    }

    response = client.post(f"/grupos/{grupo.grupo_id}/usuarios/bulk", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert len(data["created"]) == 3
    assert data["skipped"] == []
    assert user1_id in data["created"]
    assert user2_id in data["created"]
    assert user3_id in data["created"]

    # Verify all links exist in database
    for usuario_id in [user1_id, user2_id, user3_id]:
        link = db_session.query(GruposUsuarios).filter(
            GruposUsuarios.grupo_id == grupo.grupo_id,
            GruposUsuarios.usuario_id == usuario_id
        ).first()
        assert link is not None


def test_adicionar_usuarios_em_lote_com_duplicados(admin_client, db_session):
    """Test bulk adding usuarios with duplicates (idempotent behavior)."""
    client, user_id, empresa_id = admin_client

    plano = criar_plano(db_session, empresa_id)
    grupo = criar_grupo(db_session, empresa_id, plano.plano_id)

    existing_user_id = str(uuid.uuid4())
    new_user1_id = str(uuid.uuid4())
    new_user2_id = str(uuid.uuid4())

    # Pre-add one usuario
    adicionar_usuario_ao_grupo(db_session, empresa_id, grupo.grupo_id, existing_user_id)

    # Bulk add all three (1 existing + 2 new)
    payload = {
        "grupo_id": str(grupo.grupo_id),
        "empresa_id": empresa_id,
        "usuario_ids": [existing_user_id, new_user1_id, new_user2_id]
    }

    response = client.post(f"/grupos/{grupo.grupo_id}/usuarios/bulk", json=payload)

    assert response.status_code == 200
    data = response.json()

    # Verify created list has 2 new users
    assert len(data["created"]) == 2
    assert new_user1_id in data["created"]
    assert new_user2_id in data["created"]
    assert existing_user_id not in data["created"]

    # Verify skipped list has 1 existing user
    assert len(data["skipped"]) == 1
    assert data["skipped"][0]["usuario_id"] == existing_user_id
    assert data["skipped"][0]["reason"] == "already_exists"


def test_adicionar_usuarios_em_lote_grupo_inexistente(admin_client):
    """Test bulk adding usuarios to non-existent grupo returns 404."""
    client, user_id, empresa_id = admin_client

    fake_grupo_id = str(uuid.uuid4())
    user_ids = [str(uuid.uuid4()), str(uuid.uuid4())]

    payload = {
        "grupo_id": fake_grupo_id,
        "empresa_id": empresa_id,
        "usuario_ids": user_ids
    }

    response = client.post(f"/grupos/{fake_grupo_id}/usuarios/bulk", json=payload)

    assert response.status_code == 404
    assert response.json()["detail"] == "Grupo nao encontrado"

