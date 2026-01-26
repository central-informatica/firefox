"""Tests for Planos de Trabalho API endpoints."""

import uuid

from backend.app.main import app
from backend.app.api.deps import check_auth_with_ip
from tests.factories.plano_factory import criar_plano


# ---------------------------------------------------------------------------
# Helper: mock check_auth
# ---------------------------------------------------------------------------
def _mock_admin(user_id=None, org_id=None):
    """Return mock check_auth for admin user."""
    async def mock():
        return {
            "id": user_id or str(uuid.uuid4()),
            "is_admin": True,
            "organization_id": org_id or str(uuid.uuid4()),
            "email": "admin@test.com",
        }
    return mock


def _mock_user(user_id=None, org_id=None):
    """Return mock check_auth for non-admin user."""
    async def mock():
        return {
            "id": user_id or str(uuid.uuid4()),
            "is_admin": False,
            "organization_id": org_id or str(uuid.uuid4()),
            "email": "user@test.com",
        }
    return mock


# ---------------------------------------------------------------------------
# GET /planos-trabalho/
# ---------------------------------------------------------------------------
def test_listar_planos_trabalho_success(client, db_session):
    """List planos de trabalho successfully."""
    user_id = str(uuid.uuid4())
    empresa_id = str(uuid.uuid4())

    # Create test plano
    plano = criar_plano(db_session, empresa_id, nome="Plano Teste")

    app.dependency_overrides[check_auth_with_ip] = _mock_user(user_id, empresa_id)

    response = client.get("/planos-trabalho/")

    app.dependency_overrides.pop(check_auth_with_ip, None)

    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert data["total"] >= 1


def test_listar_planos_trabalho_with_empresa_id(client, db_session):
    """List planos de trabalho with specific empresa_id."""
    user_id = str(uuid.uuid4())
    empresa_id = str(uuid.uuid4())

    plano = criar_plano(db_session, empresa_id, nome="Plano Empresa Especifica")

    app.dependency_overrides[check_auth_with_ip] = _mock_user(user_id, empresa_id)

    response = client.get(f"/planos-trabalho/?empresa_id={empresa_id}")

    app.dependency_overrides.pop(check_auth_with_ip, None)

    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1


def test_listar_planos_trabalho_unauthenticated(client):
    """Unauthenticated request gets 401."""
    response = client.get("/planos-trabalho/")
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# GET /planos-trabalho/{plano_id}
# ---------------------------------------------------------------------------
def test_get_plano_trabalho_success(client, db_session):
    """Get single plano de trabalho successfully."""
    user_id = str(uuid.uuid4())
    empresa_id = str(uuid.uuid4())

    plano = criar_plano(db_session, empresa_id, nome="Plano Individual")

    app.dependency_overrides[check_auth_with_ip] = _mock_user(user_id, empresa_id)

    response = client.get(f"/planos-trabalho/{plano.plano_id}")

    app.dependency_overrides.pop(check_auth_with_ip, None)

    assert response.status_code == 200
    data = response.json()
    assert data["nome"] == "Plano Individual"


def test_get_plano_trabalho_not_found(client, db_session):
    """Get nonexistent plano returns 404."""
    user_id = str(uuid.uuid4())
    empresa_id = str(uuid.uuid4())
    fake_id = str(uuid.uuid4())

    app.dependency_overrides[check_auth_with_ip] = _mock_user(user_id, empresa_id)

    response = client.get(f"/planos-trabalho/{fake_id}")

    app.dependency_overrides.pop(check_auth_with_ip, None)

    assert response.status_code == 404


def test_get_plano_trabalho_unauthenticated(client):
    """Unauthenticated request gets 401."""
    fake_id = str(uuid.uuid4())
    response = client.get(f"/planos-trabalho/{fake_id}")
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# POST /planos-trabalho/
# ---------------------------------------------------------------------------
def test_criar_plano_trabalho_admin_success(client, db_session):
    """Admin can create plano de trabalho."""
    user_id = str(uuid.uuid4())
    empresa_id = str(uuid.uuid4())

    app.dependency_overrides[check_auth_with_ip] = _mock_admin(user_id, empresa_id)

    payload = {"nome": "Novo Plano", "descricao": "Descricao do plano"}
    response = client.post("/planos-trabalho/", json=payload)

    app.dependency_overrides.pop(check_auth_with_ip, None)

    assert response.status_code == 201
    data = response.json()
    assert data["nome"] == "Novo Plano"


def test_criar_plano_trabalho_non_admin_forbidden(client, db_session):
    """Non-admin cannot create plano de trabalho."""
    user_id = str(uuid.uuid4())
    empresa_id = str(uuid.uuid4())

    app.dependency_overrides[check_auth_with_ip] = _mock_user(user_id, empresa_id)

    payload = {"nome": "Novo Plano", "descricao": "Descricao do plano"}
    response = client.post("/planos-trabalho/", json=payload)

    app.dependency_overrides.pop(check_auth_with_ip, None)

    assert response.status_code == 403


def test_criar_plano_trabalho_unauthenticated(client):
    """Unauthenticated request gets 401."""
    payload = {"nome": "Novo Plano", "descricao": "Descricao do plano"}
    response = client.post("/planos-trabalho/", json=payload)
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# PUT /planos-trabalho/{plano_id}
# ---------------------------------------------------------------------------
def test_atualizar_plano_trabalho_admin_success(client, db_session):
    """Admin can update plano de trabalho."""
    user_id = str(uuid.uuid4())
    empresa_id = str(uuid.uuid4())

    plano = criar_plano(db_session, empresa_id, nome="Plano Original")

    app.dependency_overrides[check_auth_with_ip] = _mock_admin(user_id, empresa_id)

    payload = {"nome": "Plano Atualizado"}
    response = client.put(f"/planos-trabalho/{plano.plano_id}", json=payload)

    app.dependency_overrides.pop(check_auth_with_ip, None)

    assert response.status_code == 200
    data = response.json()
    assert data["nome"] == "Plano Atualizado"


def test_atualizar_plano_trabalho_non_admin_forbidden(client, db_session):
    """Non-admin cannot update plano de trabalho."""
    user_id = str(uuid.uuid4())
    empresa_id = str(uuid.uuid4())

    plano = criar_plano(db_session, empresa_id, nome="Plano Original")

    app.dependency_overrides[check_auth_with_ip] = _mock_user(user_id, empresa_id)

    payload = {"nome": "Plano Atualizado"}
    response = client.put(f"/planos-trabalho/{plano.plano_id}", json=payload)

    app.dependency_overrides.pop(check_auth_with_ip, None)

    assert response.status_code == 403


def test_atualizar_plano_trabalho_not_found(client, db_session):
    """Update nonexistent plano returns 404."""
    user_id = str(uuid.uuid4())
    empresa_id = str(uuid.uuid4())
    fake_id = str(uuid.uuid4())

    app.dependency_overrides[check_auth_with_ip] = _mock_admin(user_id, empresa_id)

    payload = {"nome": "Plano Atualizado"}
    response = client.put(f"/planos-trabalho/{fake_id}", json=payload)

    app.dependency_overrides.pop(check_auth_with_ip, None)

    assert response.status_code == 404


def test_atualizar_plano_trabalho_unauthenticated(client):
    """Unauthenticated request gets 401."""
    fake_id = str(uuid.uuid4())
    payload = {"nome": "Plano Atualizado"}
    response = client.put(f"/planos-trabalho/{fake_id}", json=payload)
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# DELETE /planos-trabalho/{plano_id}
# ---------------------------------------------------------------------------
def test_deletar_plano_trabalho_admin_success(client, db_session):
    """Admin can delete plano de trabalho."""
    user_id = str(uuid.uuid4())
    empresa_id = str(uuid.uuid4())

    plano = criar_plano(db_session, empresa_id, nome="Plano a Deletar")

    app.dependency_overrides[check_auth_with_ip] = _mock_admin(user_id, empresa_id)

    response = client.delete(f"/planos-trabalho/{plano.plano_id}")

    app.dependency_overrides.pop(check_auth_with_ip, None)

    assert response.status_code == 200
    assert response.json()["ok"] is True


def test_deletar_plano_trabalho_non_admin_forbidden(client, db_session):
    """Non-admin cannot delete plano de trabalho."""
    user_id = str(uuid.uuid4())
    empresa_id = str(uuid.uuid4())

    plano = criar_plano(db_session, empresa_id, nome="Plano a Deletar")

    app.dependency_overrides[check_auth_with_ip] = _mock_user(user_id, empresa_id)

    response = client.delete(f"/planos-trabalho/{plano.plano_id}")

    app.dependency_overrides.pop(check_auth_with_ip, None)

    assert response.status_code == 403


def test_deletar_plano_trabalho_not_found(client, db_session):
    """Delete nonexistent plano returns 404."""
    user_id = str(uuid.uuid4())
    empresa_id = str(uuid.uuid4())
    fake_id = str(uuid.uuid4())

    app.dependency_overrides[check_auth_with_ip] = _mock_admin(user_id, empresa_id)

    response = client.delete(f"/planos-trabalho/{fake_id}")

    app.dependency_overrides.pop(check_auth_with_ip, None)

    assert response.status_code == 404


def test_deletar_plano_trabalho_unauthenticated(client):
    """Unauthenticated request gets 401."""
    fake_id = str(uuid.uuid4())
    response = client.delete(f"/planos-trabalho/{fake_id}")
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# Uniqueness Constraint Tests
# ---------------------------------------------------------------------------

def test_criar_plano_duplicate_name_same_empresa_returns_409(client, db_session):
    """Creating plano with duplicate name in same empresa returns 409."""
    user_id = str(uuid.uuid4())
    empresa_id = str(uuid.uuid4())

    criar_plano(db_session, empresa_id, nome="Equipe Vendas")

    app.dependency_overrides[check_auth_with_ip] = _mock_admin(user_id, empresa_id)

    payload = {"nome": "Equipe Vendas", "descricao": "Duplicata"}
    response = client.post("/planos-trabalho/", json=payload)

    app.dependency_overrides.pop(check_auth_with_ip, None)

    assert response.status_code == 409
    assert "já existe" in response.json()["detail"].lower()


def test_criar_plano_same_name_different_empresa_succeeds(client, db_session):
    """Creating plano with same name in different empresa succeeds."""
    user1_id = str(uuid.uuid4())
    empresa1_id = str(uuid.uuid4())
    user2_id = str(uuid.uuid4())
    empresa2_id = str(uuid.uuid4())

    criar_plano(db_session, empresa1_id, nome="Equipe Vendas")

    app.dependency_overrides[check_auth_with_ip] = _mock_admin(user2_id, empresa2_id)

    payload = {"nome": "Equipe Vendas", "descricao": "Mesma nome, empresa diferente"}
    response = client.post("/planos-trabalho/", json=payload)

    app.dependency_overrides.pop(check_auth_with_ip, None)

    assert response.status_code == 201
    data = response.json()
    assert data["nome"] == "Equipe Vendas"
    assert data["empresa_id"] == empresa2_id


def test_atualizar_plano_duplicate_name_same_empresa_returns_409(client, db_session):
    """Updating plano to duplicate name in same empresa returns 409."""
    user_id = str(uuid.uuid4())
    empresa_id = str(uuid.uuid4())

    plano1 = criar_plano(db_session, empresa_id, nome="Plano A")
    plano2 = criar_plano(db_session, empresa_id, nome="Plano B")

    app.dependency_overrides[check_auth_with_ip] = _mock_admin(user_id, empresa_id)

    payload = {"nome": "Plano A"}
    response = client.put(f"/planos-trabalho/{plano2.plano_id}", json=payload)

    app.dependency_overrides.pop(check_auth_with_ip, None)

    assert response.status_code == 409
    assert "já existe" in response.json()["detail"].lower()


def test_atualizar_plano_same_name_keeps_same_name(client, db_session):
    """Updating plano with its own name succeeds (no-op)."""
    user_id = str(uuid.uuid4())
    empresa_id = str(uuid.uuid4())

    plano = criar_plano(db_session, empresa_id, nome="Plano Original")

    app.dependency_overrides[check_auth_with_ip] = _mock_admin(user_id, empresa_id)

    payload = {"nome": "Plano Original", "descricao": "Nova descricao"}
    response = client.put(f"/planos-trabalho/{plano.plano_id}", json=payload)

    app.dependency_overrides.pop(check_auth_with_ip, None)

    assert response.status_code == 200
    data = response.json()
    assert data["nome"] == "Plano Original"
    assert data["descricao"] == "Nova descricao"
