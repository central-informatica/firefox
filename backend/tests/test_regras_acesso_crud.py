"""
Comprehensive CRUD tests for regras_acesso endpoints.

Tests verify that admin users can successfully perform all CRUD operations
on regras de acesso endpoints.
"""

import uuid
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.api.deps import check_auth_with_ip
from backend.app.db.session import get_db
from backend.app.db.models import RegrasAcesso

from tests.factories.plano_factory import criar_plano
from tests.factories.grupo_factory import criar_grupo
from tests.factories.regra_acesso_factory import criar_regra_acesso
from tests.factories.usuarios_ip_whitelist_factory import criar_usuarios_ip_whitelist


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
# GET /regras-acesso/ - List All Rules
# ============================================

def test_list_regras_empty(admin_client):
    """Test listing regras when none exist returns empty list."""
    client, user_id, empresa_id, db_session = admin_client

    response = client.get("/regras-acesso/")

    assert response.status_code == 200
    assert response.json() == []


def test_list_regras_with_data(admin_client):
    """Test listing regras returns all created regras."""
    client, user_id, empresa_id, db_session = admin_client

    # Create plano and grupo
    plano = criar_plano(db_session, empresa_id)
    grupo = criar_grupo(db_session, empresa_id, plano.plano_id)

    # Create two regras
    regra1 = criar_regra_acesso(
        db_session,
        empresa_id=empresa_id,
        grupo_id=str(grupo.grupo_id),
        tipo_dia="corridos",
        horarios=[{"inicio": "08:00", "fim": "18:00"}],
    )
    regra2 = criar_regra_acesso(
        db_session,
        empresa_id=empresa_id,
        grupo_id=str(grupo.grupo_id),
        tipo_dia="uteis",
        horarios=[{"inicio": "09:00", "fim": "17:00"}],
    )

    response = client.get("/regras-acesso/")

    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2

    # Verify our regras are in the list
    regra_ids = [r["regra_id"] for r in data]
    assert str(regra1.regra_id) in regra_ids
    assert str(regra2.regra_id) in regra_ids


def test_list_regras_returns_correct_fields(admin_client):
    """Test that listed regras contain all expected fields."""
    client, user_id, empresa_id, db_session = admin_client

    plano = criar_plano(db_session, empresa_id)
    grupo = criar_grupo(db_session, empresa_id, plano.plano_id)

    regra = criar_regra_acesso(
        db_session,
        empresa_id=empresa_id,
        grupo_id=str(grupo.grupo_id),
        tipo_dia="corridos",
        horarios=[{"inicio": "08:00", "fim": "18:00"}],
        bloquear_em_feriado=True,
    )

    response = client.get("/regras-acesso/")

    assert response.status_code == 200
    data = response.json()

    # Find our regra
    our_regra = next((r for r in data if r["regra_id"] == str(regra.regra_id)), None)
    assert our_regra is not None

    # Verify all fields
    assert our_regra["empresa_id"] == empresa_id
    assert our_regra["grupo_id"] == str(grupo.grupo_id)
    assert our_regra["tipo_dia"] == "corridos"
    assert our_regra["horarios"] == [{"inicio": "08:00", "fim": "18:00"}]
    assert our_regra["bloquear_em_feriado"] is True
    assert "criado_em" in our_regra


# ============================================
# GET /regras-acesso/grupo/{grupo_id} - List Rules by Group
# ============================================

def test_list_regras_by_grupo_empty(admin_client):
    """Test listing regras by grupo when grupo has no regras."""
    client, user_id, empresa_id, db_session = admin_client

    plano = criar_plano(db_session, empresa_id)
    grupo = criar_grupo(db_session, empresa_id, plano.plano_id)

    response = client.get(f"/regras-acesso/grupo/{grupo.grupo_id}")

    assert response.status_code == 200
    assert response.json() == []


def test_list_regras_by_grupo_with_data(admin_client):
    """Test listing regras by grupo returns only regras for that grupo."""
    client, user_id, empresa_id, db_session = admin_client

    plano = criar_plano(db_session, empresa_id)
    grupo1 = criar_grupo(db_session, empresa_id, plano.plano_id, nome="Grupo 1")
    grupo2 = criar_grupo(db_session, empresa_id, plano.plano_id, nome="Grupo 2")

    # Create regras for both grupos
    regra1 = criar_regra_acesso(
        db_session,
        empresa_id=empresa_id,
        grupo_id=str(grupo1.grupo_id),
        tipo_dia="corridos",
        horarios=[{"inicio": "08:00", "fim": "18:00"}],
    )
    regra2 = criar_regra_acesso(
        db_session,
        empresa_id=empresa_id,
        grupo_id=str(grupo1.grupo_id),
        tipo_dia="uteis",
        horarios=[{"inicio": "09:00", "fim": "17:00"}],
    )
    regra3 = criar_regra_acesso(
        db_session,
        empresa_id=empresa_id,
        grupo_id=str(grupo2.grupo_id),
        tipo_dia="corridos",
        horarios=[{"inicio": "10:00", "fim": "16:00"}],
    )

    response = client.get(f"/regras-acesso/grupo/{grupo1.grupo_id}")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2

    regra_ids = [r["regra_id"] for r in data]
    assert str(regra1.regra_id) in regra_ids
    assert str(regra2.regra_id) in regra_ids
    assert str(regra3.regra_id) not in regra_ids


def test_list_regras_by_grupo_nonexistent(admin_client):
    """Test listing regras by nonexistent grupo returns empty list."""
    client, user_id, empresa_id, db_session = admin_client

    fake_grupo_id = str(uuid.uuid4())

    response = client.get(f"/regras-acesso/grupo/{fake_grupo_id}")

    assert response.status_code == 200
    assert response.json() == []


# ============================================
# GET /regras-acesso/{regra_id} - Get Specific Rule
# ============================================

def test_get_regra_success(admin_client):
    """Test getting a specific regra returns correct data."""
    client, user_id, empresa_id, db_session = admin_client

    plano = criar_plano(db_session, empresa_id)
    grupo = criar_grupo(db_session, empresa_id, plano.plano_id)

    regra = criar_regra_acesso(
        db_session,
        empresa_id=empresa_id,
        grupo_id=str(grupo.grupo_id),
        tipo_dia="especificos",
        dias_especificos=[1, 2, 3, 4, 5],  # Monday to Friday
        horarios=[{"inicio": "08:00", "fim": "12:00"}, {"inicio": "14:00", "fim": "18:00"}],
        bloquear_em_feriado=True,
    )

    response = client.get(f"/regras-acesso/{regra.regra_id}")

    assert response.status_code == 200
    data = response.json()

    assert data["regra_id"] == str(regra.regra_id)
    assert data["empresa_id"] == empresa_id
    assert data["grupo_id"] == str(grupo.grupo_id)
    assert data["tipo_dia"] == "especificos"
    assert data["dias_especificos"] == [1, 2, 3, 4, 5]
    assert len(data["horarios"]) == 2
    assert data["horarios"][0] == {"inicio": "08:00", "fim": "12:00"}
    assert data["horarios"][1] == {"inicio": "14:00", "fim": "18:00"}
    assert data["bloquear_em_feriado"] is True
    assert "criado_em" in data


def test_get_regra_not_found(admin_client):
    """Test getting nonexistent regra returns 404."""
    client, user_id, empresa_id, db_session = admin_client

    fake_regra_id = str(uuid.uuid4())

    response = client.get(f"/regras-acesso/{fake_regra_id}")

    assert response.status_code == 404
    assert "não encontrada" in response.json()["detail"].lower()


# ============================================
# POST /regras-acesso/ - Create Rule
# ============================================

def test_create_regra_corridos(admin_client):
    """Test creating regra with tipo_dia corridos."""
    client, user_id, empresa_id, db_session = admin_client

    plano = criar_plano(db_session, empresa_id)
    grupo = criar_grupo(db_session, empresa_id, plano.plano_id)

    payload = {
        "empresa_id": empresa_id,
        "grupo_id": str(grupo.grupo_id),
        "tipo_dia": "corridos",
        "horarios": [{"inicio": "08:00", "fim": "18:00"}],
        "bloquear_em_feriado": False,
    }

    response = client.post("/regras-acesso/", json=payload)

    assert response.status_code == 201
    data = response.json()

    assert "regra_id" in data
    assert data["empresa_id"] == empresa_id
    assert data["grupo_id"] == str(grupo.grupo_id)
    assert data["tipo_dia"] == "corridos"
    assert data["horarios"] == [{"inicio": "08:00", "fim": "18:00"}]
    assert data["bloquear_em_feriado"] is False
    assert data["dias_especificos"] is None


def test_create_regra_uteis(admin_client):
    """Test creating regra with tipo_dia uteis."""
    client, user_id, empresa_id, db_session = admin_client

    plano = criar_plano(db_session, empresa_id)
    grupo = criar_grupo(db_session, empresa_id, plano.plano_id)

    payload = {
        "empresa_id": empresa_id,
        "grupo_id": str(grupo.grupo_id),
        "tipo_dia": "uteis",
        "horarios": [{"inicio": "09:00", "fim": "17:00"}],
    }

    response = client.post("/regras-acesso/", json=payload)

    assert response.status_code == 201
    data = response.json()

    assert data["tipo_dia"] == "uteis"
    assert data["dias_especificos"] is None


def test_create_regra_especificos(admin_client):
    """Test creating regra with tipo_dia especificos."""
    client, user_id, empresa_id, db_session = admin_client

    plano = criar_plano(db_session, empresa_id)
    grupo = criar_grupo(db_session, empresa_id, plano.plano_id)

    payload = {
        "empresa_id": empresa_id,
        "grupo_id": str(grupo.grupo_id),
        "tipo_dia": "especificos",
        "dias_especificos": [1, 3, 5],  # Monday, Wednesday, Friday
        "horarios": [{"inicio": "10:00", "fim": "16:00"}],
    }

    response = client.post("/regras-acesso/", json=payload)

    assert response.status_code == 201
    data = response.json()

    assert data["tipo_dia"] == "especificos"
    assert data["dias_especificos"] == [1, 3, 5]


def test_create_regra_persisted_in_database(admin_client):
    """Test that created regra is actually persisted in database."""
    client, user_id, empresa_id, db_session = admin_client

    plano = criar_plano(db_session, empresa_id)
    grupo = criar_grupo(db_session, empresa_id, plano.plano_id)

    payload = {
        "empresa_id": empresa_id,
        "grupo_id": str(grupo.grupo_id),
        "tipo_dia": "corridos",
        "horarios": [{"inicio": "08:00", "fim": "18:00"}],
    }

    response = client.post("/regras-acesso/", json=payload)

    assert response.status_code == 201
    regra_id = response.json()["regra_id"]

    # Verify in database
    db_regra = db_session.query(RegrasAcesso).filter(
        RegrasAcesso.regra_id == regra_id
    ).first()

    assert db_regra is not None
    assert str(db_regra.empresa_id) == empresa_id
    assert str(db_regra.grupo_id) == str(grupo.grupo_id)
    assert db_regra.tipo_dia == "corridos"


def test_create_regra_multiple_horarios(admin_client):
    """Test creating regra with multiple time ranges."""
    client, user_id, empresa_id, db_session = admin_client

    plano = criar_plano(db_session, empresa_id)
    grupo = criar_grupo(db_session, empresa_id, plano.plano_id)

    payload = {
        "empresa_id": empresa_id,
        "grupo_id": str(grupo.grupo_id),
        "tipo_dia": "corridos",
        "horarios": [
            {"inicio": "08:00", "fim": "12:00"},
            {"inicio": "14:00", "fim": "18:00"},
            {"inicio": "19:00", "fim": "22:00"},
        ],
    }

    response = client.post("/regras-acesso/", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert len(data["horarios"]) == 3


def test_create_regra_especificos_without_dias_fails(admin_client):
    """Test creating especificos regra without dias_especificos fails validation."""
    client, user_id, empresa_id, db_session = admin_client

    plano = criar_plano(db_session, empresa_id)
    grupo = criar_grupo(db_session, empresa_id, plano.plano_id)

    payload = {
        "empresa_id": empresa_id,
        "grupo_id": str(grupo.grupo_id),
        "tipo_dia": "especificos",
        "horarios": [{"inicio": "08:00", "fim": "18:00"}],
    }

    response = client.post("/regras-acesso/", json=payload)

    assert response.status_code == 422
    assert "dias_especificos" in str(response.json()).lower()


def test_create_regra_invalid_horarios_format(admin_client):
    """Test creating regra with invalid horarios format fails."""
    client, user_id, empresa_id, db_session = admin_client

    plano = criar_plano(db_session, empresa_id)
    grupo = criar_grupo(db_session, empresa_id, plano.plano_id)

    payload = {
        "empresa_id": empresa_id,
        "grupo_id": str(grupo.grupo_id),
        "tipo_dia": "corridos",
        "horarios": [{"inicio": "08:00"}],  # Missing 'fim'
    }

    response = client.post("/regras-acesso/", json=payload)

    assert response.status_code == 422


def test_create_regra_empty_horarios_fails(admin_client):
    """Test creating regra with empty horarios list fails."""
    client, user_id, empresa_id, db_session = admin_client

    plano = criar_plano(db_session, empresa_id)
    grupo = criar_grupo(db_session, empresa_id, plano.plano_id)

    payload = {
        "empresa_id": empresa_id,
        "grupo_id": str(grupo.grupo_id),
        "tipo_dia": "corridos",
        "horarios": [],
    }

    response = client.post("/regras-acesso/", json=payload)

    assert response.status_code == 422


def test_create_regra_missing_required_fields(admin_client):
    """Test creating regra without required fields fails."""
    client, user_id, empresa_id, db_session = admin_client

    payload = {
        "empresa_id": empresa_id,
        # Missing grupo_id, tipo_dia, horarios
    }

    response = client.post("/regras-acesso/", json=payload)

    assert response.status_code == 422


# ============================================
# PUT /regras-acesso/{regra_id} - Update Rule
# ============================================

def test_update_regra_success(admin_client):
    """Test updating regra returns updated data."""
    client, user_id, empresa_id, db_session = admin_client

    plano = criar_plano(db_session, empresa_id)
    grupo = criar_grupo(db_session, empresa_id, plano.plano_id)

    regra = criar_regra_acesso(
        db_session,
        empresa_id=empresa_id,
        grupo_id=str(grupo.grupo_id),
        tipo_dia="corridos",
        horarios=[{"inicio": "08:00", "fim": "18:00"}],
        bloquear_em_feriado=False,
    )

    update_payload = {
        "horarios": [{"inicio": "09:00", "fim": "17:00"}],
        "bloquear_em_feriado": True,
    }

    response = client.put(f"/regras-acesso/{regra.regra_id}", json=update_payload)

    assert response.status_code == 200
    data = response.json()

    assert data["regra_id"] == str(regra.regra_id)
    assert data["horarios"] == [{"inicio": "09:00", "fim": "17:00"}]
    assert data["bloquear_em_feriado"] is True
    assert data["tipo_dia"] == "corridos"  # Unchanged


def test_update_regra_partial_update(admin_client):
    """Test partial update (only updating horarios)."""
    client, user_id, empresa_id, db_session = admin_client

    plano = criar_plano(db_session, empresa_id)
    grupo = criar_grupo(db_session, empresa_id, plano.plano_id)

    regra = criar_regra_acesso(
        db_session,
        empresa_id=empresa_id,
        grupo_id=str(grupo.grupo_id),
        tipo_dia="corridos",
        horarios=[{"inicio": "08:00", "fim": "18:00"}],
        bloquear_em_feriado=False,
    )

    update_payload = {
        "horarios": [{"inicio": "10:00", "fim": "16:00"}],
    }

    response = client.put(f"/regras-acesso/{regra.regra_id}", json=update_payload)

    assert response.status_code == 200
    data = response.json()

    assert data["horarios"] == [{"inicio": "10:00", "fim": "16:00"}]
    assert data["bloquear_em_feriado"] is False  # Unchanged


def test_update_regra_tipo_dia_to_especificos(admin_client):
    """Test updating tipo_dia to especificos with dias_especificos."""
    client, user_id, empresa_id, db_session = admin_client

    plano = criar_plano(db_session, empresa_id)
    grupo = criar_grupo(db_session, empresa_id, plano.plano_id)

    regra = criar_regra_acesso(
        db_session,
        empresa_id=empresa_id,
        grupo_id=str(grupo.grupo_id),
        tipo_dia="corridos",
        horarios=[{"inicio": "08:00", "fim": "18:00"}],
    )

    update_payload = {
        "tipo_dia": "especificos",
        "dias_especificos": [2, 4, 6],  # Tuesday, Thursday, Saturday
    }

    response = client.put(f"/regras-acesso/{regra.regra_id}", json=update_payload)

    assert response.status_code == 200
    data = response.json()

    assert data["tipo_dia"] == "especificos"
    assert data["dias_especificos"] == [2, 4, 6]


def test_update_regra_tipo_dia_to_especificos_without_dias_fails(admin_client):
    """Test updating to especificos without dias_especificos fails."""
    client, user_id, empresa_id, db_session = admin_client

    plano = criar_plano(db_session, empresa_id)
    grupo = criar_grupo(db_session, empresa_id, plano.plano_id)

    regra = criar_regra_acesso(
        db_session,
        empresa_id=empresa_id,
        grupo_id=str(grupo.grupo_id),
        tipo_dia="corridos",
        horarios=[{"inicio": "08:00", "fim": "18:00"}],
    )

    update_payload = {
        "tipo_dia": "especificos",
    }

    response = client.put(f"/regras-acesso/{regra.regra_id}", json=update_payload)

    assert response.status_code == 400
    assert "dias_especificos" in response.json()["detail"].lower()


def test_update_regra_persisted_in_database(admin_client):
    """Test that updates are persisted in database."""
    client, user_id, empresa_id, db_session = admin_client

    plano = criar_plano(db_session, empresa_id)
    grupo = criar_grupo(db_session, empresa_id, plano.plano_id)

    regra = criar_regra_acesso(
        db_session,
        empresa_id=empresa_id,
        grupo_id=str(grupo.grupo_id),
        tipo_dia="corridos",
        horarios=[{"inicio": "08:00", "fim": "18:00"}],
        bloquear_em_feriado=False,
    )

    update_payload = {
        "bloquear_em_feriado": True,
    }

    response = client.put(f"/regras-acesso/{regra.regra_id}", json=update_payload)
    assert response.status_code == 200

    # Refresh from database
    db_session.refresh(regra)

    assert regra.bloquear_em_feriado is True


def test_update_regra_not_found(admin_client):
    """Test updating nonexistent regra returns 404."""
    client, user_id, empresa_id, db_session = admin_client

    fake_regra_id = str(uuid.uuid4())

    update_payload = {
        "horarios": [{"inicio": "09:00", "fim": "17:00"}],
    }

    response = client.put(f"/regras-acesso/{fake_regra_id}", json=update_payload)

    assert response.status_code == 404


def test_update_regra_invalid_horarios_format(admin_client):
    """Test updating with invalid horarios format fails."""
    client, user_id, empresa_id, db_session = admin_client

    plano = criar_plano(db_session, empresa_id)
    grupo = criar_grupo(db_session, empresa_id, plano.plano_id)

    regra = criar_regra_acesso(
        db_session,
        empresa_id=empresa_id,
        grupo_id=str(grupo.grupo_id),
        tipo_dia="corridos",
        horarios=[{"inicio": "08:00", "fim": "18:00"}],
    )

    update_payload = {
        "horarios": [{"inicio": "09:00"}],  # Missing 'fim'
    }

    response = client.put(f"/regras-acesso/{regra.regra_id}", json=update_payload)

    assert response.status_code == 422


# ============================================
# DELETE /regras-acesso/{regra_id} - Delete Rule
# ============================================

def test_delete_regra_success(admin_client):
    """Test deleting regra returns success status."""
    client, user_id, empresa_id, db_session = admin_client

    plano = criar_plano(db_session, empresa_id)
    grupo = criar_grupo(db_session, empresa_id, plano.plano_id)

    regra = criar_regra_acesso(
        db_session,
        empresa_id=empresa_id,
        grupo_id=str(grupo.grupo_id),
        tipo_dia="corridos",
        horarios=[{"inicio": "08:00", "fim": "18:00"}],
    )

    response = client.delete(f"/regras-acesso/{regra.regra_id}")

    assert response.status_code == 200
    assert response.json()["status"] == "deleted"


def test_delete_regra_removed_from_database(admin_client):
    """Test that deleted regra is removed from database."""
    client, user_id, empresa_id, db_session = admin_client

    plano = criar_plano(db_session, empresa_id)
    grupo = criar_grupo(db_session, empresa_id, plano.plano_id)

    regra = criar_regra_acesso(
        db_session,
        empresa_id=empresa_id,
        grupo_id=str(grupo.grupo_id),
        tipo_dia="corridos",
        horarios=[{"inicio": "08:00", "fim": "18:00"}],
    )
    regra_id = str(regra.regra_id)

    response = client.delete(f"/regras-acesso/{regra_id}")
    assert response.status_code == 200

    # Verify removed from database
    db_regra = db_session.query(RegrasAcesso).filter(
        RegrasAcesso.regra_id == regra_id
    ).first()

    assert db_regra is None


def test_delete_regra_not_found(admin_client):
    """Test deleting nonexistent regra returns 404."""
    client, user_id, empresa_id, db_session = admin_client

    fake_regra_id = str(uuid.uuid4())

    response = client.delete(f"/regras-acesso/{fake_regra_id}")

    assert response.status_code == 404


def test_delete_regra_twice_fails(admin_client):
    """Test deleting same regra twice fails on second attempt."""
    client, user_id, empresa_id, db_session = admin_client

    plano = criar_plano(db_session, empresa_id)
    grupo = criar_grupo(db_session, empresa_id, plano.plano_id)

    regra = criar_regra_acesso(
        db_session,
        empresa_id=empresa_id,
        grupo_id=str(grupo.grupo_id),
        tipo_dia="corridos",
        horarios=[{"inicio": "08:00", "fim": "18:00"}],
    )

    # First delete
    response1 = client.delete(f"/regras-acesso/{regra.regra_id}")
    assert response1.status_code == 200

    # Second delete should fail
    response2 = client.delete(f"/regras-acesso/{regra.regra_id}")
    assert response2.status_code == 404
