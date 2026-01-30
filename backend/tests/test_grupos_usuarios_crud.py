"""
Comprehensive CRUD tests for grupos_usuarios endpoints.

Tests verify that admin users can successfully perform all CRUD operations
on both /grupos-usuarios/* and /grupos/{id}/usuarios/* endpoints.
"""

import uuid
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.api.deps import check_auth_with_ip
from backend.app.db.session import get_db
from backend.app.db.models import GruposUsuarios

from tests.factories.plano_factory import criar_plano
from tests.factories.grupo_factory import criar_grupo
from tests.factories.grupo_usuario_factory import adicionar_usuario_ao_grupo
from tests.factories.usuarios_ip_whitelist_factory import criar_usuarios_ip_whitelist
from tests.factories.usuario_factory import get_mock_usuario_id
from tests.factories.empresa_factory import get_mock_empresa_id


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
        yield test_client, user_id, empresa_id, db_session

    app.dependency_overrides.clear()


# ============================================
# GET /grupos-usuarios/ - List All Relationships
# ============================================

def test_list_grupos_usuarios_empty(admin_client):
    """Test listing grupos-usuarios when none exist returns empty list."""
    client, user_id, empresa_id, db_session = admin_client

    response = client.get("/grupos-usuarios/")

    assert response.status_code == 200
    assert response.json() == []


def test_list_grupos_usuarios_with_data(admin_client):
    """Test listing grupos-usuarios returns all relationships."""
    client, user_id, empresa_id, db_session = admin_client

    # Create test data with mock IDs
    test_empresa_id = get_mock_empresa_id()

    plano = criar_plano(db_session, test_empresa_id)
    grupo1 = criar_grupo(db_session, test_empresa_id, plano.plano_id, nome="Grupo 1")
    grupo2 = criar_grupo(db_session, test_empresa_id, plano.plano_id, nome="Grupo 2")

    usuario1_id = get_mock_usuario_id()
    usuario2_id = get_mock_usuario_id()

    # Add users to groups
    rel1 = adicionar_usuario_ao_grupo(db_session, test_empresa_id, grupo1.grupo_id, usuario1_id)
    rel2 = adicionar_usuario_ao_grupo(db_session, test_empresa_id, grupo2.grupo_id, usuario2_id)

    response = client.get("/grupos-usuarios/")

    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2

    # Verify our relationships are in the list
    rel_ids = [r["grupo_usuario_id"] for r in data]
    assert str(rel1.grupo_usuario_id) in rel_ids
    assert str(rel2.grupo_usuario_id) in rel_ids


def test_list_grupos_usuarios_returns_correct_fields(admin_client):
    """Test that listed relationships contain all expected fields."""
    client, user_id, empresa_id, db_session = admin_client

    test_empresa_id = get_mock_empresa_id()
    plano = criar_plano(db_session, test_empresa_id)
    grupo = criar_grupo(db_session, test_empresa_id, plano.plano_id)

    usuario_id = get_mock_usuario_id()
    rel = adicionar_usuario_ao_grupo(db_session, test_empresa_id, grupo.grupo_id, usuario_id)

    response = client.get("/grupos-usuarios/")

    assert response.status_code == 200
    data = response.json()

    # Find our relationship
    our_rel = next((r for r in data if r["grupo_usuario_id"] == str(rel.grupo_usuario_id)), None)
    assert our_rel is not None
    assert our_rel["grupo_id"] == str(grupo.grupo_id)


# ============================================
# GET /grupos-usuarios/grupo/{grupo_id} - List by Group
# ============================================

def test_list_grupos_usuarios_by_grupo_empty(admin_client):
    """Test listing by grupo when grupo has no users."""
    client, user_id, empresa_id, db_session = admin_client

    test_empresa_id = get_mock_empresa_id()
    plano = criar_plano(db_session, test_empresa_id)
    grupo = criar_grupo(db_session, test_empresa_id, plano.plano_id)

    response = client.get(f"/grupos-usuarios/grupo/{grupo.grupo_id}")

    assert response.status_code == 200
    assert response.json() == []


def test_list_grupos_usuarios_by_grupo_with_data(admin_client):
    """Test listing by grupo returns only relationships for that grupo."""
    client, user_id, empresa_id, db_session = admin_client

    test_empresa_id = get_mock_empresa_id()
    plano = criar_plano(db_session, test_empresa_id)
    grupo1 = criar_grupo(db_session, test_empresa_id, plano.plano_id, nome="Grupo 1")
    grupo2 = criar_grupo(db_session, test_empresa_id, plano.plano_id, nome="Grupo 2")

    usuario1_id = get_mock_usuario_id()
    usuario2_id = get_mock_usuario_id()
    usuario3_id = get_mock_usuario_id()

    # Add users to groups
    rel1 = adicionar_usuario_ao_grupo(db_session, test_empresa_id, grupo1.grupo_id, usuario1_id)
    rel2 = adicionar_usuario_ao_grupo(db_session, test_empresa_id, grupo1.grupo_id, usuario2_id)
    rel3 = adicionar_usuario_ao_grupo(db_session, test_empresa_id, grupo2.grupo_id, usuario3_id)

    response = client.get(f"/grupos-usuarios/grupo/{grupo1.grupo_id}")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2

    rel_ids = [r["grupo_usuario_id"] for r in data]
    assert str(rel1.grupo_usuario_id) in rel_ids
    assert str(rel2.grupo_usuario_id) in rel_ids
    assert str(rel3.grupo_usuario_id) not in rel_ids


def test_list_grupos_usuarios_by_grupo_nonexistent(admin_client):
    """Test listing by nonexistent grupo returns empty list."""
    client, user_id, empresa_id, db_session = admin_client

    fake_grupo_id = str(uuid.uuid4())

    response = client.get(f"/grupos-usuarios/grupo/{fake_grupo_id}")

    assert response.status_code == 200
    assert response.json() == []


# ============================================
# GET /grupos-usuarios/{grupo_usuario_id} - Get Specific
# ============================================

def test_get_grupo_usuario_success(admin_client):
    """Test getting a specific grupo-usuario relationship returns correct data."""
    client, user_id, empresa_id, db_session = admin_client

    test_empresa_id = get_mock_empresa_id()
    plano = criar_plano(db_session, test_empresa_id)
    grupo = criar_grupo(db_session, test_empresa_id, plano.plano_id)

    usuario_id = get_mock_usuario_id()
    rel = adicionar_usuario_ao_grupo(db_session, test_empresa_id, grupo.grupo_id, usuario_id)

    response = client.get(f"/grupos-usuarios/{rel.grupo_usuario_id}")

    assert response.status_code == 200
    data = response.json()

    assert data["grupo_usuario_id"] == str(rel.grupo_usuario_id)
    assert data["grupo_id"] == str(grupo.grupo_id)


def test_get_grupo_usuario_not_found(admin_client):
    """Test getting nonexistent relationship returns 404."""
    client, user_id, empresa_id, db_session = admin_client

    fake_id = str(uuid.uuid4())

    response = client.get(f"/grupos-usuarios/{fake_id}")

    assert response.status_code == 404
    assert "não encontrada" in response.json()["detail"].lower()


# ============================================
# POST /grupos-usuarios/ - Create Single Relationship
# ============================================

def test_create_grupo_usuario_success(admin_client):
    """Test creating a grupo-usuario relationship."""
    client, user_id, empresa_id, db_session = admin_client

    test_empresa_id = get_mock_empresa_id()
    plano = criar_plano(db_session, test_empresa_id)
    grupo = criar_grupo(db_session, test_empresa_id, plano.plano_id)

    usuario_id = get_mock_usuario_id()

    payload = {
        "grupo_id": str(grupo.grupo_id),
        "usuario_id": usuario_id,
        "empresa_id": test_empresa_id,
    }

    response = client.post("/grupos-usuarios/", json=payload)

    assert response.status_code == 201
    data = response.json()

    assert "grupo_usuario_id" in data
    assert data["grupo_id"] == str(grupo.grupo_id)


def test_create_grupo_usuario_persisted_in_database(admin_client):
    """Test that created relationship is actually persisted in database."""
    client, user_id, empresa_id, db_session = admin_client

    test_empresa_id = get_mock_empresa_id()
    plano = criar_plano(db_session, test_empresa_id)
    grupo = criar_grupo(db_session, test_empresa_id, plano.plano_id)

    usuario_id = get_mock_usuario_id()

    payload = {
        "grupo_id": str(grupo.grupo_id),
        "usuario_id": usuario_id,
        "empresa_id": test_empresa_id,
    }

    response = client.post("/grupos-usuarios/", json=payload)
    assert response.status_code == 201

    grupo_usuario_id = response.json()["grupo_usuario_id"]

    # Verify in database
    db_rel = db_session.query(GruposUsuarios).filter(
        GruposUsuarios.grupo_usuario_id == grupo_usuario_id
    ).first()

    assert db_rel is not None
    assert str(db_rel.grupo_id) == str(grupo.grupo_id)
    assert str(db_rel.usuario_id) == usuario_id


def test_create_grupo_usuario_missing_fields(admin_client):
    """Test creating relationship without required fields fails."""
    client, user_id, empresa_id, db_session = admin_client

    payload = {
        "grupo_id": str(uuid.uuid4()),
        # Missing usuario_id
    }

    response = client.post("/grupos-usuarios/", json=payload)

    assert response.status_code == 422


# ============================================
# POST /grupos-usuarios/bulk - Bulk Create
# ============================================

def test_create_grupos_usuarios_bulk_success(admin_client):
    """Test bulk creating grupo-usuario relationships."""
    client, user_id, empresa_id, db_session = admin_client

    test_empresa_id = get_mock_empresa_id()
    plano = criar_plano(db_session, test_empresa_id)
    grupo = criar_grupo(db_session, test_empresa_id, plano.plano_id)

    usuario1_id = get_mock_usuario_id()
    usuario2_id = get_mock_usuario_id()
    usuario3_id = get_mock_usuario_id()

    payload = {
        "grupo_id": str(grupo.grupo_id),
        "usuario_ids": [usuario1_id, usuario2_id, usuario3_id],
        "empresa_id": test_empresa_id,
    }

    response = client.post("/grupos-usuarios/bulk", json=payload)

    assert response.status_code == 200
    data = response.json()

    assert "created" in data
    assert "skipped" in data
    assert len(data["created"]) == 3
    assert len(data["skipped"]) == 0


def test_create_grupos_usuarios_bulk_with_duplicates(admin_client):
    """Test bulk create skips duplicates."""
    client, user_id, empresa_id, db_session = admin_client

    test_empresa_id = get_mock_empresa_id()
    plano = criar_plano(db_session, test_empresa_id)
    grupo = criar_grupo(db_session, test_empresa_id, plano.plano_id)

    usuario1_id = get_mock_usuario_id()
    usuario2_id = get_mock_usuario_id()

    # Pre-add usuario1 to grupo
    adicionar_usuario_ao_grupo(db_session, test_empresa_id, grupo.grupo_id, usuario1_id)

    payload = {
        "grupo_id": str(grupo.grupo_id),
        "usuario_ids": [usuario1_id, usuario2_id],
        "empresa_id": test_empresa_id,
    }

    response = client.post("/grupos-usuarios/bulk", json=payload)

    assert response.status_code == 200
    data = response.json()

    assert len(data["created"]) == 1
    assert usuario2_id in data["created"]
    assert len(data["skipped"]) == 1
    assert data["skipped"][0]["usuario_id"] == usuario1_id
    assert data["skipped"][0]["reason"] == "already_exists"


def test_create_grupos_usuarios_bulk_empty_list(admin_client):
    """Test bulk create with empty usuario_ids list."""
    client, user_id, empresa_id, db_session = admin_client

    test_empresa_id = get_mock_empresa_id()
    plano = criar_plano(db_session, test_empresa_id)
    grupo = criar_grupo(db_session, test_empresa_id, plano.plano_id)

    payload = {
        "grupo_id": str(grupo.grupo_id),
        "usuario_ids": [],
        "empresa_id": test_empresa_id,
    }

    response = client.post("/grupos-usuarios/bulk", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert len(data["created"]) == 0
    assert len(data["skipped"]) == 0


def test_create_grupos_usuarios_bulk_persisted(admin_client):
    """Test that bulk created relationships are persisted in database."""
    client, user_id, empresa_id, db_session = admin_client

    test_empresa_id = get_mock_empresa_id()
    plano = criar_plano(db_session, test_empresa_id)
    grupo = criar_grupo(db_session, test_empresa_id, plano.plano_id)

    usuario1_id = get_mock_usuario_id()
    usuario2_id = get_mock_usuario_id()

    payload = {
        "grupo_id": str(grupo.grupo_id),
        "usuario_ids": [usuario1_id, usuario2_id],
        "empresa_id": test_empresa_id,
    }

    response = client.post("/grupos-usuarios/bulk", json=payload)
    assert response.status_code == 200

    # Verify in database
    db_rels = db_session.query(GruposUsuarios).filter(
        GruposUsuarios.grupo_id == grupo.grupo_id
    ).all()

    assert len(db_rels) == 2
    db_usuario_ids = [str(r.usuario_id) for r in db_rels]
    assert usuario1_id in db_usuario_ids
    assert usuario2_id in db_usuario_ids


# ============================================
# POST /grupos/{grupo_id}/usuarios/bulk - Bulk Add to Group
# ============================================

def test_add_usuarios_bulk_to_grupo_success(admin_client):
    """Test bulk adding usuarios to grupo via /grupos/{id}/usuarios/bulk endpoint."""
    client, user_id, empresa_id, db_session = admin_client

    test_empresa_id = get_mock_empresa_id()
    plano = criar_plano(db_session, test_empresa_id)
    grupo = criar_grupo(db_session, test_empresa_id, plano.plano_id)

    usuario1_id = get_mock_usuario_id()
    usuario2_id = get_mock_usuario_id()

    payload = {
        "grupo_id": str(grupo.grupo_id),  # Required by GrupoUsuarioBulkCreate schema
        "usuario_ids": [usuario1_id, usuario2_id],
        "empresa_id": test_empresa_id,
    }

    response = client.post(f"/grupos/{grupo.grupo_id}/usuarios/bulk", json=payload)

    assert response.status_code == 200
    data = response.json()

    assert len(data["created"]) == 2
    assert len(data["skipped"]) == 0


def test_add_usuarios_bulk_to_grupo_with_duplicates(admin_client):
    """Test bulk add to grupo skips duplicates."""
    client, user_id, empresa_id, db_session = admin_client

    test_empresa_id = get_mock_empresa_id()
    plano = criar_plano(db_session, test_empresa_id)
    grupo = criar_grupo(db_session, test_empresa_id, plano.plano_id)

    usuario1_id = get_mock_usuario_id()
    usuario2_id = get_mock_usuario_id()

    # Pre-add usuario1
    adicionar_usuario_ao_grupo(db_session, test_empresa_id, grupo.grupo_id, usuario1_id)

    payload = {
        "grupo_id": str(grupo.grupo_id),  # Required by GrupoUsuarioBulkCreate schema
        "usuario_ids": [usuario1_id, usuario2_id],
        "empresa_id": test_empresa_id,
    }

    response = client.post(f"/grupos/{grupo.grupo_id}/usuarios/bulk", json=payload)

    assert response.status_code == 200
    data = response.json()

    assert len(data["created"]) == 1
    assert usuario2_id in data["created"]
    assert len(data["skipped"]) == 1


def test_add_usuarios_bulk_to_nonexistent_grupo(admin_client):
    """Test bulk add to nonexistent grupo returns 404."""
    client, user_id, empresa_id, db_session = admin_client

    fake_grupo_id = str(uuid.uuid4())

    payload = {
        "grupo_id": fake_grupo_id,  # Required by GrupoUsuarioBulkCreate schema
        "usuario_ids": [str(uuid.uuid4())],
        "empresa_id": empresa_id,
    }

    response = client.post(f"/grupos/{fake_grupo_id}/usuarios/bulk", json=payload)

    assert response.status_code == 404


# ============================================
# PUT /grupos-usuarios/{grupo_usuario_id} - Update
# ============================================

def test_update_grupo_usuario_success(admin_client):
    """Test updating a grupo-usuario relationship."""
    client, user_id, empresa_id, db_session = admin_client

    test_empresa_id = get_mock_empresa_id()
    plano = criar_plano(db_session, test_empresa_id)
    grupo1 = criar_grupo(db_session, test_empresa_id, plano.plano_id, nome="Grupo 1")
    grupo2 = criar_grupo(db_session, test_empresa_id, plano.plano_id, nome="Grupo 2")

    usuario_id = get_mock_usuario_id()
    rel = adicionar_usuario_ao_grupo(db_session, test_empresa_id, grupo1.grupo_id, usuario_id)

    update_payload = {
        "grupo_id": str(grupo2.grupo_id),
    }

    response = client.put(f"/grupos-usuarios/{rel.grupo_usuario_id}", json=update_payload)

    assert response.status_code == 200
    data = response.json()

    assert data["grupo_usuario_id"] == str(rel.grupo_usuario_id)
    assert data["grupo_id"] == str(grupo2.grupo_id)


def test_update_grupo_usuario_persisted(admin_client):
    """Test that updates are persisted in database."""
    client, user_id, empresa_id, db_session = admin_client

    test_empresa_id = get_mock_empresa_id()
    plano = criar_plano(db_session, test_empresa_id)
    grupo1 = criar_grupo(db_session, test_empresa_id, plano.plano_id, nome="Grupo 1")
    grupo2 = criar_grupo(db_session, test_empresa_id, plano.plano_id, nome="Grupo 2")

    usuario_id = get_mock_usuario_id()
    rel = adicionar_usuario_ao_grupo(db_session, test_empresa_id, grupo1.grupo_id, usuario_id)

    update_payload = {
        "grupo_id": str(grupo2.grupo_id),
    }

    response = client.put(f"/grupos-usuarios/{rel.grupo_usuario_id}", json=update_payload)
    assert response.status_code == 200

    # Verify in database
    db_session.refresh(rel)
    assert str(rel.grupo_id) == str(grupo2.grupo_id)


def test_update_grupo_usuario_not_found(admin_client):
    """Test updating nonexistent relationship returns 404."""
    client, user_id, empresa_id, db_session = admin_client

    fake_id = str(uuid.uuid4())

    update_payload = {
        "grupo_id": str(uuid.uuid4()),
    }

    response = client.put(f"/grupos-usuarios/{fake_id}", json=update_payload)

    assert response.status_code == 404


# ============================================
# DELETE /grupos-usuarios/{grupo_usuario_id} - Delete
# ============================================

def test_delete_grupo_usuario_success(admin_client):
    """Test deleting a grupo-usuario relationship."""
    client, user_id, empresa_id, db_session = admin_client

    test_empresa_id = get_mock_empresa_id()
    plano = criar_plano(db_session, test_empresa_id)
    grupo = criar_grupo(db_session, test_empresa_id, plano.plano_id)

    usuario_id = get_mock_usuario_id()
    rel = adicionar_usuario_ao_grupo(db_session, test_empresa_id, grupo.grupo_id, usuario_id)

    response = client.delete(f"/grupos-usuarios/{rel.grupo_usuario_id}")

    assert response.status_code == 200
    assert response.json()["status"] == "deleted"


def test_delete_grupo_usuario_removed_from_database(admin_client):
    """Test that deleted relationship is removed from database."""
    client, user_id, empresa_id, db_session = admin_client

    test_empresa_id = get_mock_empresa_id()
    plano = criar_plano(db_session, test_empresa_id)
    grupo = criar_grupo(db_session, test_empresa_id, plano.plano_id)

    usuario_id = get_mock_usuario_id()
    rel = adicionar_usuario_ao_grupo(db_session, test_empresa_id, grupo.grupo_id, usuario_id)
    rel_id = str(rel.grupo_usuario_id)

    response = client.delete(f"/grupos-usuarios/{rel_id}")
    assert response.status_code == 200

    # Verify removed from database
    db_rel = db_session.query(GruposUsuarios).filter(
        GruposUsuarios.grupo_usuario_id == rel_id
    ).first()

    assert db_rel is None


def test_delete_grupo_usuario_not_found(admin_client):
    """Test deleting nonexistent relationship returns 404."""
    client, user_id, empresa_id, db_session = admin_client

    fake_id = str(uuid.uuid4())

    response = client.delete(f"/grupos-usuarios/{fake_id}")

    assert response.status_code == 404


def test_delete_grupo_usuario_twice_fails(admin_client):
    """Test deleting same relationship twice fails on second attempt."""
    client, user_id, empresa_id, db_session = admin_client

    test_empresa_id = get_mock_empresa_id()
    plano = criar_plano(db_session, test_empresa_id)
    grupo = criar_grupo(db_session, test_empresa_id, plano.plano_id)

    usuario_id = get_mock_usuario_id()
    rel = adicionar_usuario_ao_grupo(db_session, test_empresa_id, grupo.grupo_id, usuario_id)

    # First delete
    response1 = client.delete(f"/grupos-usuarios/{rel.grupo_usuario_id}")
    assert response1.status_code == 200

    # Second delete should fail
    response2 = client.delete(f"/grupos-usuarios/{rel.grupo_usuario_id}")
    assert response2.status_code == 404
