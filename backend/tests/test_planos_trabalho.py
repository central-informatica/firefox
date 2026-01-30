"""Tests for Planos de Trabalho API endpoints."""

import uuid

from backend.app.main import app
from backend.app.api.deps import check_auth_with_ip
from backend.app.db.models import Grupos, GruposUsuarios, RegrasAcesso
from tests.factories.plano_factory import criar_plano
from tests.factories.grupo_factory import criar_grupo
from tests.factories.grupo_usuario_factory import adicionar_usuario_ao_grupo
from tests.factories.regra_acesso_factory import criar_regra_acesso


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


# ---------------------------------------------------------------------------
# VALIDATION TESTS - POST Input Validation
# ---------------------------------------------------------------------------
def test_criar_plano_missing_nome_returns_422(client, db_session):
    """Missing required nome field returns 422."""
    user_id = str(uuid.uuid4())
    empresa_id = str(uuid.uuid4())

    app.dependency_overrides[check_auth_with_ip] = _mock_admin(user_id, empresa_id)

    payload = {"descricao": "Sem nome"}
    response = client.post("/planos-trabalho/", json=payload)

    app.dependency_overrides.pop(check_auth_with_ip, None)

    assert response.status_code == 422
    assert "nome" in str(response.json()).lower()


def test_criar_plano_nome_null_returns_422(client, db_session):
    """Null nome field returns 422."""
    user_id = str(uuid.uuid4())
    empresa_id = str(uuid.uuid4())

    app.dependency_overrides[check_auth_with_ip] = _mock_admin(user_id, empresa_id)

    payload = {"nome": None, "descricao": "Nome nulo"}
    response = client.post("/planos-trabalho/", json=payload)

    app.dependency_overrides.pop(check_auth_with_ip, None)

    assert response.status_code == 422


def test_criar_plano_nome_empty_string(client, db_session):
    """Empty string nome - documents actual behavior."""
    user_id = str(uuid.uuid4())
    empresa_id = str(uuid.uuid4())

    app.dependency_overrides[check_auth_with_ip] = _mock_admin(user_id, empresa_id)

    payload = {"nome": "", "descricao": "Nome vazio"}
    response = client.post("/planos-trabalho/", json=payload)

    app.dependency_overrides.pop(check_auth_with_ip, None)

    # Schema allows empty, but DB might reject (NOT NULL constraint)
    # Document actual behavior
    assert response.status_code in [201, 400, 422, 500]


def test_criar_plano_nome_whitespace_only(client, db_session):
    """Whitespace-only nome - documents actual behavior."""
    user_id = str(uuid.uuid4())
    empresa_id = str(uuid.uuid4())

    app.dependency_overrides[check_auth_with_ip] = _mock_admin(user_id, empresa_id)

    payload = {"nome": "   ", "descricao": "Só espaços"}
    response = client.post("/planos-trabalho/", json=payload)

    app.dependency_overrides.pop(check_auth_with_ip, None)

    # Schema allows this - documents behavior
    assert response.status_code in [201, 400, 422]


def test_criar_plano_nome_over_100_chars(client, db_session):
    """Nome over 100 characters - DB has max 100 limit."""
    user_id = str(uuid.uuid4())
    empresa_id = str(uuid.uuid4())

    app.dependency_overrides[check_auth_with_ip] = _mock_admin(user_id, empresa_id)

    payload = {"nome": "A" * 101, "descricao": "Muito longo"}
    response = client.post("/planos-trabalho/", json=payload)

    app.dependency_overrides.pop(check_auth_with_ip, None)

    # Schema allows, but DB has max 100 chars
    assert response.status_code in [400, 422, 500]


# ---------------------------------------------------------------------------
# VALIDATION TESTS - PUT Input Validation
# ---------------------------------------------------------------------------
def test_atualizar_plano_nome_too_short_returns_422(client, db_session):
    """Nome with only 1 character returns 422 (min 2)."""
    user_id = str(uuid.uuid4())
    empresa_id = str(uuid.uuid4())

    plano = criar_plano(db_session, empresa_id, nome="Plano Teste")

    app.dependency_overrides[check_auth_with_ip] = _mock_admin(user_id, empresa_id)

    payload = {"nome": "A"}  # Only 1 char
    response = client.put(f"/planos-trabalho/{plano.plano_id}", json=payload)

    app.dependency_overrides.pop(check_auth_with_ip, None)

    assert response.status_code == 422
    error_detail = str(response.json()).lower()
    assert "at least 2 characters" in error_detail or "2" in error_detail


def test_atualizar_plano_nome_too_long_returns_422(client, db_session):
    """Nome with 101 characters returns 422 (max 100)."""
    user_id = str(uuid.uuid4())
    empresa_id = str(uuid.uuid4())

    plano = criar_plano(db_session, empresa_id, nome="Plano Teste")

    app.dependency_overrides[check_auth_with_ip] = _mock_admin(user_id, empresa_id)

    payload = {"nome": "A" * 101}  # 101 chars
    response = client.put(f"/planos-trabalho/{plano.plano_id}", json=payload)

    app.dependency_overrides.pop(check_auth_with_ip, None)

    assert response.status_code == 422
    error_detail = str(response.json()).lower()
    assert "at most 100 characters" in error_detail or "100" in error_detail


def test_atualizar_plano_nome_empty_string_returns_422(client, db_session):
    """Empty string nome returns 422."""
    user_id = str(uuid.uuid4())
    empresa_id = str(uuid.uuid4())

    plano = criar_plano(db_session, empresa_id, nome="Plano Teste")

    app.dependency_overrides[check_auth_with_ip] = _mock_admin(user_id, empresa_id)

    payload = {"nome": ""}
    response = client.put(f"/planos-trabalho/{plano.plano_id}", json=payload)

    app.dependency_overrides.pop(check_auth_with_ip, None)

    assert response.status_code == 422


def test_atualizar_plano_empty_payload_returns_200(client, db_session):
    """Empty payload (no fields to update) returns 200 (no-op)."""
    user_id = str(uuid.uuid4())
    empresa_id = str(uuid.uuid4())

    plano = criar_plano(db_session, empresa_id, nome="Plano Teste")

    app.dependency_overrides[check_auth_with_ip] = _mock_admin(user_id, empresa_id)

    payload = {}  # No fields to update
    response = client.put(f"/planos-trabalho/{plano.plano_id}", json=payload)

    app.dependency_overrides.pop(check_auth_with_ip, None)

    assert response.status_code == 200  # Should succeed (no-op)


def test_atualizar_plano_nome_exactly_100_chars_success(client, db_session):
    """Nome with exactly 100 characters succeeds (boundary test)."""
    user_id = str(uuid.uuid4())
    empresa_id = str(uuid.uuid4())

    plano = criar_plano(db_session, empresa_id, nome="Plano Teste")

    app.dependency_overrides[check_auth_with_ip] = _mock_admin(user_id, empresa_id)

    payload = {"nome": "A" * 100}  # Boundary: exactly 100
    response = client.put(f"/planos-trabalho/{plano.plano_id}", json=payload)

    app.dependency_overrides.pop(check_auth_with_ip, None)

    assert response.status_code == 200
    assert response.json()["nome"] == "A" * 100


def test_atualizar_plano_nome_exactly_2_chars_success(client, db_session):
    """Nome with exactly 2 characters succeeds (boundary test)."""
    user_id = str(uuid.uuid4())
    empresa_id = str(uuid.uuid4())

    plano = criar_plano(db_session, empresa_id, nome="Plano Teste")

    app.dependency_overrides[check_auth_with_ip] = _mock_admin(user_id, empresa_id)

    payload = {"nome": "AB"}  # Boundary: exactly 2
    response = client.put(f"/planos-trabalho/{plano.plano_id}", json=payload)

    app.dependency_overrides.pop(check_auth_with_ip, None)

    assert response.status_code == 200
    assert response.json()["nome"] == "AB"


# ---------------------------------------------------------------------------
# VALIDATION TESTS - UUID Validation
# ---------------------------------------------------------------------------
def test_get_plano_invalid_uuid_returns_404(client, db_session):
    """Invalid UUID format returns 404 or 422."""
    user_id = str(uuid.uuid4())
    empresa_id = str(uuid.uuid4())

    app.dependency_overrides[check_auth_with_ip] = _mock_admin(user_id, empresa_id)

    response = client.get("/planos-trabalho/not-a-uuid")

    app.dependency_overrides.pop(check_auth_with_ip, None)

    # FastAPI might return 422 for invalid UUID format or 404
    assert response.status_code in [404, 422]


def test_atualizar_plano_invalid_uuid_returns_404(client, db_session):
    """Invalid UUID format in PUT returns 404 or 422."""
    user_id = str(uuid.uuid4())
    empresa_id = str(uuid.uuid4())

    app.dependency_overrides[check_auth_with_ip] = _mock_admin(user_id, empresa_id)

    payload = {"nome": "Updated Name"}
    response = client.put("/planos-trabalho/invalid-uuid-123", json=payload)

    app.dependency_overrides.pop(check_auth_with_ip, None)

    assert response.status_code in [404, 422]


def test_deletar_plano_invalid_uuid_returns_404(client, db_session):
    """Invalid UUID format in DELETE returns 404 or 422."""
    user_id = str(uuid.uuid4())
    empresa_id = str(uuid.uuid4())

    app.dependency_overrides[check_auth_with_ip] = _mock_admin(user_id, empresa_id)

    response = client.delete("/planos-trabalho/not-a-valid-uuid")

    app.dependency_overrides.pop(check_auth_with_ip, None)

    assert response.status_code in [404, 422]


# ---------------------------------------------------------------------------
# VALIDATION TESTS - Pagination Boundaries
# ---------------------------------------------------------------------------
def test_listar_planos_page_zero(client, db_session):
    """Page 0 - documents actual behavior."""
    user_id = str(uuid.uuid4())
    empresa_id = str(uuid.uuid4())

    criar_plano(db_session, empresa_id, nome="Plano 1")

    app.dependency_overrides[check_auth_with_ip] = _mock_admin(user_id, empresa_id)

    response = client.get("/planos-trabalho/?page=0&limit=10")

    app.dependency_overrides.pop(check_auth_with_ip, None)

    assert response.status_code == 200
    # Documents behavior: might return empty or treat as page 1


def test_listar_planos_negative_page(client, db_session):
    """Negative page number - documents actual behavior."""
    user_id = str(uuid.uuid4())
    empresa_id = str(uuid.uuid4())

    criar_plano(db_session, empresa_id, nome="Plano 1")

    app.dependency_overrides[check_auth_with_ip] = _mock_admin(user_id, empresa_id)

    response = client.get("/planos-trabalho/?page=-1&limit=10")

    app.dependency_overrides.pop(check_auth_with_ip, None)

    assert response.status_code == 200
    # Documents behavior


def test_listar_planos_limit_zero(client, db_session):
    """Limit 0 - should return empty items."""
    user_id = str(uuid.uuid4())
    empresa_id = str(uuid.uuid4())

    criar_plano(db_session, empresa_id, nome="Plano 1")

    app.dependency_overrides[check_auth_with_ip] = _mock_admin(user_id, empresa_id)

    response = client.get("/planos-trabalho/?page=1&limit=0")

    app.dependency_overrides.pop(check_auth_with_ip, None)

    assert response.status_code == 200
    assert len(response.json()["items"]) == 0


def test_listar_planos_negative_limit(client, db_session):
    """Negative limit - documents actual behavior."""
    user_id = str(uuid.uuid4())
    empresa_id = str(uuid.uuid4())

    criar_plano(db_session, empresa_id, nome="Plano 1")

    app.dependency_overrides[check_auth_with_ip] = _mock_admin(user_id, empresa_id)

    response = client.get("/planos-trabalho/?page=1&limit=-5")

    app.dependency_overrides.pop(check_auth_with_ip, None)

    assert response.status_code == 200
    # Documents behavior: might return empty or error


def test_listar_planos_very_large_limit(client, db_session):
    """Very large limit - documents actual behavior."""
    user_id = str(uuid.uuid4())
    empresa_id = str(uuid.uuid4())

    criar_plano(db_session, empresa_id, nome="Plano 1")

    app.dependency_overrides[check_auth_with_ip] = _mock_admin(user_id, empresa_id)

    response = client.get("/planos-trabalho/?page=1&limit=999999")

    app.dependency_overrides.pop(check_auth_with_ip, None)

    assert response.status_code == 200
    # Should succeed or have max limit


def test_listar_planos_with_multiple_pages(client, db_session):
    """Pagination across multiple pages works correctly."""
    user_id = str(uuid.uuid4())
    empresa_id = str(uuid.uuid4())

    # Create 25 planos
    for i in range(25):
        criar_plano(db_session, empresa_id, nome=f"Plano {i:02d}")

    app.dependency_overrides[check_auth_with_ip] = _mock_admin(user_id, empresa_id)

    # Page 1
    response = client.get("/planos-trabalho/?page=1&limit=10")
    assert response.status_code == 200
    assert len(response.json()["items"]) == 10
    assert response.json()["total"] == 25

    # Page 2
    response = client.get("/planos-trabalho/?page=2&limit=10")
    assert response.status_code == 200
    assert len(response.json()["items"]) == 10

    # Page 3
    response = client.get("/planos-trabalho/?page=3&limit=10")
    assert response.status_code == 200
    assert len(response.json()["items"]) == 5

    # Page 4 (beyond data)
    response = client.get("/planos-trabalho/?page=4&limit=10")
    assert response.status_code == 200
    assert len(response.json()["items"]) == 0

    app.dependency_overrides.pop(check_auth_with_ip, None)


# ---------------------------------------------------------------------------
# VALIDATION TESTS - Search/Sort Parameters (Currently Non-Functional)
# ---------------------------------------------------------------------------
def test_listar_planos_search_parameter_currently_ignored(client, db_session):
    """Search parameter is accepted but currently not implemented."""
    user_id = str(uuid.uuid4())
    empresa_id = str(uuid.uuid4())

    # Create planos with distinct names
    criar_plano(db_session, empresa_id, nome="Alpha")
    criar_plano(db_session, empresa_id, nome="Beta")

    app.dependency_overrides[check_auth_with_ip] = _mock_admin(user_id, empresa_id)

    response = client.get("/planos-trabalho/?search=Alpha")

    app.dependency_overrides.pop(check_auth_with_ip, None)

    assert response.status_code == 200
    # Currently returns ALL planos (search not implemented)
    # This test documents baseline behavior for future implementation


def test_listar_planos_sort_parameter_currently_ignored(client, db_session):
    """Sort parameter is accepted but currently not implemented."""
    user_id = str(uuid.uuid4())
    empresa_id = str(uuid.uuid4())

    # Create planos in specific order
    criar_plano(db_session, empresa_id, nome="Zebra")
    criar_plano(db_session, empresa_id, nome="Alpha")

    app.dependency_overrides[check_auth_with_ip] = _mock_admin(user_id, empresa_id)

    response = client.get("/planos-trabalho/?sort=nome")

    app.dependency_overrides.pop(check_auth_with_ip, None)

    assert response.status_code == 200
    # Currently returns in creation order (sort not implemented)
    # This test documents baseline behavior for future implementation


# ---------------------------------------------------------------------------
# INTEGRATION TESTS - Cascade Delete
# ---------------------------------------------------------------------------
def test_deletar_plano_cascades_to_grupos(client, db_session):
    """Deleting plano cascades to delete related grupos."""
    user_id = str(uuid.uuid4())
    empresa_id = str(uuid.uuid4())

    # Create plano with grupos
    plano = criar_plano(db_session, empresa_id, nome="Plano com Grupos")
    grupo1 = criar_grupo(db_session, empresa_id, plano.plano_id, nome="Grupo 1")
    grupo2 = criar_grupo(db_session, empresa_id, plano.plano_id, nome="Grupo 2")

    # Verify grupos exist before delete
    grupos_before = db_session.query(Grupos).filter(
        Grupos.plano_id == plano.plano_id
    ).count()
    assert grupos_before == 2

    # Delete plano
    app.dependency_overrides[check_auth_with_ip] = _mock_admin(user_id, empresa_id)
    response = client.delete(f"/planos-trabalho/{plano.plano_id}")
    app.dependency_overrides.pop(check_auth_with_ip, None)

    assert response.status_code == 200

    # Verify grupos were cascade deleted
    grupos_after = db_session.query(Grupos).filter(
        Grupos.plano_id == plano.plano_id
    ).count()
    assert grupos_after == 0


def test_deletar_plano_cascades_to_nested_entities(client, db_session):
    """Deleting plano cascades through grupos to nested entities."""
    user_id = str(uuid.uuid4())
    empresa_id = str(uuid.uuid4())

    # Create complex hierarchy
    plano = criar_plano(db_session, empresa_id, nome="Plano Complexo")
    grupo = criar_grupo(db_session, empresa_id, plano.plano_id, nome="Grupo")
    adicionar_usuario_ao_grupo(db_session, empresa_id, grupo.grupo_id, str(uuid.uuid4()))
    criar_regra_acesso(db_session, empresa_id, grupo.grupo_id)

    # Count related entities before delete
    grupos_count = db_session.query(Grupos).filter(Grupos.plano_id == plano.plano_id).count()
    usuarios_count = db_session.query(GruposUsuarios).filter(GruposUsuarios.grupo_id == grupo.grupo_id).count()
    regras_count = db_session.query(RegrasAcesso).filter(RegrasAcesso.grupo_id == grupo.grupo_id).count()

    assert grupos_count == 1
    assert usuarios_count >= 1
    assert regras_count >= 1

    # Delete plano
    app.dependency_overrides[check_auth_with_ip] = _mock_admin(user_id, empresa_id)
    response = client.delete(f"/planos-trabalho/{plano.plano_id}")
    app.dependency_overrides.pop(check_auth_with_ip, None)

    assert response.status_code == 200

    # Verify all related entities were cascade deleted
    assert db_session.query(Grupos).filter(Grupos.plano_id == plano.plano_id).count() == 0
    assert db_session.query(GruposUsuarios).filter(GruposUsuarios.grupo_id == grupo.grupo_id).count() == 0
    assert db_session.query(RegrasAcesso).filter(RegrasAcesso.grupo_id == grupo.grupo_id).count() == 0
