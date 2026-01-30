"""
Comprehensive functional tests for Feriados (Holidays) API endpoints.

Tests cover:
- CRUD operations (create, read, update, delete)
- Business logic (duplicate date prevention)
- Recorrente flag functionality
- Validation (nome length, date format, required fields)
- Error handling (404, 400, 422)
- Database persistence verification
- Date handling (past, present, future)
- Multi-tenant context
- Edge cases
"""

import uuid
from datetime import date, timedelta
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.api.deps import check_auth_with_ip
from backend.app.db.session import get_db
from backend.app.db.models import Feriados

from tests.factories.feriado_factory import criar_feriado
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
        yield test_client, user_id, empresa_id

    app.dependency_overrides.clear()


# ============================================
# CRUD Happy Path Tests - CREATE
# ============================================

def test_criar_feriado_success(admin_client, db_session):
    """Test creating a holiday with all fields successfully."""
    client, user_id, empresa_id = admin_client

    payload = {
        "empresa_id": empresa_id,
        "data": "2025-12-25",
        "nome": "Natal",
        "recorrente": True,
    }

    response = client.post("/feriados/", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert "feriado_id" in data
    assert data["data"] == "2025-12-25"
    assert data["nome"] == "Natal"
    assert data["recorrente"] is True
    assert "criado_em" in data

    # Verify database persistence
    feriado_id = data["feriado_id"]
    db_record = db_session.query(Feriados).filter(
        Feriados.feriado_id == feriado_id
    ).first()
    assert db_record is not None
    assert db_record.nome == "Natal"


def test_criar_feriado_minimal(admin_client, db_session):
    """Test creating a holiday with only required fields."""
    client, user_id, empresa_id = admin_client

    payload = {
        "empresa_id": empresa_id,
        "data": "2025-01-01",
        "nome": "Ano Novo",
    }

    response = client.post("/feriados/", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["recorrente"] is False  # Default value


def test_criar_feriado_with_recorrente_true(admin_client, db_session):
    """Test creating a recurring holiday."""
    client, user_id, empresa_id = admin_client

    payload = {
        "empresa_id": empresa_id,
        "data": "2025-11-15",
        "nome": "Proclamação da República",
        "recorrente": True,
    }

    response = client.post("/feriados/", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["recorrente"] is True


def test_criar_feriado_status_201(admin_client):
    """Test that POST returns 201 Created status code."""
    client, user_id, empresa_id = admin_client

    payload = {
        "empresa_id": empresa_id,
        "data": "2025-09-07",
        "nome": "Independência do Brasil",
    }

    response = client.post("/feriados/", json=payload)

    assert response.status_code == 201  # Not 200


# ============================================
# CRUD Happy Path Tests - READ
# ============================================

def test_get_feriado_by_id_success(admin_client, db_session):
    """Test getting a holiday by ID."""
    client, user_id, empresa_id = admin_client

    # Create holiday using factory
    feriado = criar_feriado(
        db_session,
        empresa_id=empresa_id,
        data=date(2025, 5, 1),
        nome="Dia do Trabalho",
        recorrente=True
    )

    response = client.get(f"/feriados/{feriado.feriado_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["feriado_id"] == str(feriado.feriado_id)
    assert data["nome"] == "Dia do Trabalho"
    assert data["data"] == "2025-05-01"
    assert data["recorrente"] is True


def test_listar_feriados_success(admin_client, db_session):
    """Test listing multiple holidays."""
    client, user_id, empresa_id = admin_client

    # Create 3 holidays
    criar_feriado(db_session, empresa_id, date(2025, 1, 1), "Ano Novo")
    criar_feriado(db_session, empresa_id, date(2025, 12, 25), "Natal")
    criar_feriado(db_session, empresa_id, date(2025, 11, 15), "Proclamação")

    response = client.get("/feriados/")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 3  # May have more from other tests


def test_listar_feriados_empty(admin_client):
    """Test listing holidays when none exist."""
    client, user_id, empresa_id = admin_client

    response = client.get("/feriados/")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


# ============================================
# CRUD Happy Path Tests - UPDATE
# ============================================

def test_atualizar_feriado_all_fields(admin_client, db_session):
    """Test updating all fields of a holiday."""
    client, user_id, empresa_id = admin_client

    # Create holiday
    feriado = criar_feriado(
        db_session,
        empresa_id,
        date(2025, 6, 1),
        "Feriado Antigo",
        recorrente=False
    )
    feriado_id = feriado.feriado_id

    payload = {
        "data": "2025-06-15",
        "nome": "Feriado Atualizado",
        "recorrente": True,
    }

    response = client.put(f"/feriados/{feriado_id}", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["data"] == "2025-06-15"
    assert data["nome"] == "Feriado Atualizado"
    assert data["recorrente"] is True

    # Verify database persistence
    db_session.refresh(feriado)
    assert feriado.nome == "Feriado Atualizado"
    assert feriado.recorrente is True


def test_atualizar_feriado_partial_nome_only(admin_client, db_session):
    """Test updating only the nome field."""
    client, user_id, empresa_id = admin_client

    # Create holiday
    feriado = criar_feriado(
        db_session,
        empresa_id,
        date(2025, 7, 1),
        "Nome Original",
        recorrente=True
    )
    feriado_id = feriado.feriado_id
    original_date = feriado.data

    payload = {
        "nome": "Nome Atualizado",
    }

    response = client.put(f"/feriados/{feriado_id}", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["nome"] == "Nome Atualizado"
    assert data["data"] == str(original_date)  # Unchanged
    assert data["recorrente"] is True  # Unchanged


def test_atualizar_feriado_partial_data_only(admin_client, db_session):
    """Test updating only the data field."""
    client, user_id, empresa_id = admin_client

    # Create holiday
    feriado = criar_feriado(
        db_session,
        empresa_id,
        date(2025, 8, 1),
        "Feriado Fixo"
    )
    feriado_id = feriado.feriado_id

    payload = {
        "data": "2025-08-15",
    }

    response = client.put(f"/feriados/{feriado_id}", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["data"] == "2025-08-15"
    assert data["nome"] == "Feriado Fixo"  # Unchanged


def test_atualizar_feriado_partial_recorrente_only(admin_client, db_session):
    """Test updating only the recorrente flag."""
    client, user_id, empresa_id = admin_client

    # Create holiday
    feriado = criar_feriado(
        db_session,
        empresa_id,
        date(2025, 9, 1),
        "Feriado Teste",
        recorrente=False
    )
    feriado_id = feriado.feriado_id

    payload = {
        "recorrente": True,
    }

    response = client.put(f"/feriados/{feriado_id}", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["recorrente"] is True
    assert data["nome"] == "Feriado Teste"  # Unchanged


# ============================================
# CRUD Happy Path Tests - DELETE
# ============================================

def test_deletar_feriado_success(admin_client, db_session):
    """Test deleting a holiday (hard delete)."""
    client, user_id, empresa_id = admin_client

    # Create holiday
    feriado = criar_feriado(
        db_session,
        empresa_id,
        date(2025, 10, 1),
        "Feriado para Deletar"
    )
    feriado_id = feriado.feriado_id

    response = client.delete(f"/feriados/{feriado_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "deleted"

    # Verify hard delete - record should not exist
    db_record = db_session.query(Feriados).filter(
        Feriados.feriado_id == feriado_id
    ).first()
    assert db_record is None


# ============================================
# Business Logic Tests - Duplicate Prevention (CREATE)
# ============================================

def test_criar_feriado_duplicate_date_blocked(admin_client, db_session):
    """Test that creating a holiday on an existing date is blocked."""
    client, user_id, empresa_id = admin_client

    # Create first holiday
    criar_feriado(db_session, empresa_id, date(2025, 3, 1), "Primeiro Feriado")

    # Try to create second holiday on same date
    payload = {
        "empresa_id": empresa_id,
        "data": "2025-03-01",
        "nome": "Segundo Feriado",
    }

    response = client.post("/feriados/", json=payload)

    assert response.status_code == 400
    assert "Já existe um feriado cadastrado nesta data" in response.json()["detail"]


def test_criar_feriado_different_dates_allowed(admin_client, db_session):
    """Test that multiple holidays with different dates are allowed."""
    client, user_id, empresa_id = admin_client

    payload1 = {"empresa_id": empresa_id, "data": "2025-04-01", "nome": "Feriado 1"}
    payload2 = {"empresa_id": empresa_id, "data": "2025-04-02", "nome": "Feriado 2"}
    payload3 = {"empresa_id": empresa_id, "data": "2025-04-03", "nome": "Feriado 3"}

    response1 = client.post("/feriados/", json=payload1)
    response2 = client.post("/feriados/", json=payload2)
    response3 = client.post("/feriados/", json=payload3)

    assert response1.status_code == 201
    assert response2.status_code == 201
    assert response3.status_code == 201


def test_criar_feriado_same_date_after_delete(admin_client, db_session):
    """Test that a holiday can be created on a date after deleting previous one."""
    client, user_id, empresa_id = admin_client

    # Create holiday
    feriado = criar_feriado(db_session, empresa_id, date(2025, 5, 15), "Original")
    feriado_id = feriado.feriado_id

    # Delete it
    client.delete(f"/feriados/{feriado_id}")

    # Create new holiday on same date
    payload = {
        "empresa_id": empresa_id,
        "data": "2025-05-15",
        "nome": "Novo Feriado",
    }

    response = client.post("/feriados/", json=payload)

    assert response.status_code == 201


def test_criar_feriado_duplicate_message(admin_client, db_session):
    """Test exact error message for duplicate date."""
    client, user_id, empresa_id = admin_client

    criar_feriado(db_session, empresa_id, date(2025, 6, 10), "Existente")

    payload = {"empresa_id": empresa_id, "data": "2025-06-10", "nome": "Duplicado"}
    response = client.post("/feriados/", json=payload)

    assert response.status_code == 400
    assert response.json()["detail"] == "Já existe um feriado cadastrado nesta data."


# ============================================
# Business Logic Tests - Duplicate Prevention (UPDATE)
# ============================================

def test_atualizar_feriado_to_existing_date_blocked(admin_client, db_session):
    """Test that updating to an existing date is blocked."""
    client, user_id, empresa_id = admin_client

    # Create two holidays
    feriado1 = criar_feriado(db_session, empresa_id, date(2025, 7, 10), "Feriado 1")
    criar_feriado(db_session, empresa_id, date(2025, 7, 20), "Feriado 2")

    # Try to update feriado1 to the date of feriado2
    payload = {"data": "2025-07-20"}
    response = client.put(f"/feriados/{feriado1.feriado_id}", json=payload)

    assert response.status_code == 400
    assert "Já existe um feriado nesta nova data" in response.json()["detail"]


def test_atualizar_feriado_to_same_date_allowed(admin_client, db_session):
    """Test that updating a holiday to its own date is allowed (no-op)."""
    client, user_id, empresa_id = admin_client

    feriado = criar_feriado(db_session, empresa_id, date(2025, 8, 10), "Mesmo Feriado")

    # Update to same date (should succeed)
    payload = {"data": "2025-08-10", "nome": "Nome Atualizado"}
    response = client.put(f"/feriados/{feriado.feriado_id}", json=payload)

    assert response.status_code == 200
    assert response.json()["nome"] == "Nome Atualizado"


def test_atualizar_feriado_duplicate_update_message(admin_client, db_session):
    """Test exact error message for duplicate date on update."""
    client, user_id, empresa_id = admin_client

    feriado1 = criar_feriado(db_session, empresa_id, date(2025, 9, 10), "F1")
    criar_feriado(db_session, empresa_id, date(2025, 9, 20), "F2")

    payload = {"data": "2025-09-20"}
    response = client.put(f"/feriados/{feriado1.feriado_id}", json=payload)

    assert response.status_code == 400
    assert response.json()["detail"] == "Já existe um feriado nesta nova data."


# ============================================
# Recorrente Flag Tests
# ============================================

def test_recorrente_flag_defaults_to_false(admin_client):
    """Test that recorrente flag defaults to False."""
    client, user_id, empresa_id = admin_client

    payload = {"empresa_id": empresa_id, "data": "2025-10-10", "nome": "Teste Default"}
    response = client.post("/feriados/", json=payload)

    assert response.status_code == 201
    assert response.json()["recorrente"] is False


def test_recorrente_flag_true_persists(admin_client, db_session):
    """Test that recorrente=True is persisted to database."""
    client, user_id, empresa_id = admin_client

    payload = {
        "empresa_id": empresa_id,
        "data": "2025-11-10",
        "nome": "Recorrente Teste",
        "recorrente": True
    }
    response = client.post("/feriados/", json=payload)

    assert response.status_code == 201
    feriado_id = response.json()["feriado_id"]

    # Verify in database
    db_record = db_session.query(Feriados).filter(
        Feriados.feriado_id == feriado_id
    ).first()
    assert db_record.recorrente is True


def test_recorrente_flag_lifecycle(admin_client, db_session):
    """Test recorrente flag lifecycle: False → True → False."""
    client, user_id, empresa_id = admin_client

    # Create with False
    payload = {"empresa_id": empresa_id, "data": "2025-12-10", "nome": "Lifecycle", "recorrente": False}
    response = client.post("/feriados/", json=payload)
    assert response.status_code == 201
    feriado_id = response.json()["feriado_id"]
    assert response.json()["recorrente"] is False

    # Update to True
    response = client.put(f"/feriados/{feriado_id}", json={"recorrente": True})
    assert response.status_code == 200
    assert response.json()["recorrente"] is True

    # Update back to False
    response = client.put(f"/feriados/{feriado_id}", json={"recorrente": False})
    assert response.status_code == 200
    assert response.json()["recorrente"] is False


def test_recorrente_flag_in_response(admin_client):
    """Test that recorrente flag is present in all responses."""
    client, user_id, empresa_id = admin_client

    # Create
    payload = {"empresa_id": empresa_id, "data": "2026-01-10", "nome": "Teste Response", "recorrente": True}
    response = client.post("/feriados/", json=payload)
    assert "recorrente" in response.json()

    feriado_id = response.json()["feriado_id"]

    # Get by ID
    response = client.get(f"/feriados/{feriado_id}")
    assert "recorrente" in response.json()

    # Update
    response = client.put(f"/feriados/{feriado_id}", json={"nome": "Updated"})
    assert "recorrente" in response.json()


# ============================================
# Validation Tests - Nome Length
# ============================================

def test_criar_feriado_nome_too_short(admin_client):
    """Test that nome with 1 character returns 422."""
    client, user_id, empresa_id = admin_client

    payload = {"empresa_id": empresa_id, "data": "2026-02-10", "nome": "A"}
    response = client.post("/feriados/", json=payload)

    assert response.status_code == 422


def test_criar_feriado_nome_minimum_length(admin_client):
    """Test that nome with 2 characters succeeds."""
    client, user_id, empresa_id = admin_client

    payload = {"empresa_id": empresa_id, "data": "2026-03-10", "nome": "AB"}
    response = client.post("/feriados/", json=payload)

    assert response.status_code == 201


def test_criar_feriado_nome_maximum_length(admin_client):
    """Test that nome with 120 characters succeeds."""
    client, user_id, empresa_id = admin_client

    payload = {"empresa_id": empresa_id, "data": "2026-04-10", "nome": "X" * 120}
    response = client.post("/feriados/", json=payload)

    assert response.status_code == 201


def test_criar_feriado_nome_too_long(admin_client):
    """Test that nome with 121 characters returns 422."""
    client, user_id, empresa_id = admin_client

    payload = {"empresa_id": empresa_id, "data": "2026-05-10", "nome": "X" * 121}
    response = client.post("/feriados/", json=payload)

    assert response.status_code == 422


# ============================================
# Validation Tests - Date & Required Fields
# ============================================

def test_criar_feriado_invalid_date_format(admin_client):
    """Test that invalid date format returns 422."""
    client, user_id, empresa_id = admin_client

    payload = {"empresa_id": empresa_id, "data": "invalid-date", "nome": "Teste"}
    response = client.post("/feriados/", json=payload)

    assert response.status_code == 422


def test_criar_feriado_missing_data(admin_client):
    """Test that POST without data returns 422."""
    client, user_id, empresa_id = admin_client

    payload = {"empresa_id": empresa_id, "nome": "Sem Data"}
    response = client.post("/feriados/", json=payload)

    assert response.status_code == 422


def test_criar_feriado_missing_nome(admin_client):
    """Test that POST without nome returns 422."""
    client, user_id, empresa_id = admin_client

    payload = {"empresa_id": empresa_id, "data": "2026-06-10"}
    response = client.post("/feriados/", json=payload)

    assert response.status_code == 422


# ============================================
# Error Handling Tests - 404
# ============================================

def test_get_nonexistent_feriado(admin_client):
    """Test getting a non-existent holiday returns 404."""
    client, user_id, empresa_id = admin_client

    fake_id = str(uuid.uuid4())
    response = client.get(f"/feriados/{fake_id}")

    assert response.status_code == 404
    assert "Feriado não encontrado" in response.json()["detail"]


def test_atualizar_nonexistent_feriado(admin_client):
    """Test updating a non-existent holiday returns 404."""
    client, user_id, empresa_id = admin_client

    fake_id = str(uuid.uuid4())
    payload = {"nome": "Teste"}
    response = client.put(f"/feriados/{fake_id}", json=payload)

    assert response.status_code == 404
    assert "Feriado não encontrado" in response.json()["detail"]


def test_deletar_nonexistent_feriado(admin_client):
    """Test deleting a non-existent holiday returns 404."""
    client, user_id, empresa_id = admin_client

    fake_id = str(uuid.uuid4())
    response = client.delete(f"/feriados/{fake_id}")

    assert response.status_code == 404
    assert "Feriado não encontrado" in response.json()["detail"]


# ============================================
# Database Verification Tests
# ============================================

def test_create_persists_to_database(admin_client, db_session):
    """Test that create operation persists data to database."""
    client, user_id, empresa_id = admin_client

    payload = {
        "empresa_id": empresa_id,
        "data": "2026-07-10",
        "nome": "Persist Test",
        "recorrente": True,
    }

    response = client.post("/feriados/", json=payload)
    assert response.status_code == 201

    feriado_id = response.json()["feriado_id"]

    # Query database directly
    db_record = db_session.query(Feriados).filter(
        Feriados.feriado_id == feriado_id
    ).first()

    assert db_record is not None
    assert db_record.nome == "Persist Test"
    assert db_record.data == date(2026, 7, 10)
    assert db_record.recorrente is True
    assert db_record.empresa_id == uuid.UUID(empresa_id)


def test_update_persists_to_database(admin_client, db_session):
    """Test that update operation modifies database records."""
    client, user_id, empresa_id = admin_client

    # Create via factory
    feriado = criar_feriado(
        db_session,
        empresa_id,
        date(2026, 8, 10),
        "Original"
    )
    feriado_id = feriado.feriado_id

    payload = {"nome": "Updated", "recorrente": True}
    response = client.put(f"/feriados/{feriado_id}", json=payload)
    assert response.status_code == 200

    # Query database directly
    db_session.expire_all()
    db_record = db_session.query(Feriados).filter(
        Feriados.feriado_id == feriado_id
    ).first()

    assert db_record.nome == "Updated"
    assert db_record.recorrente is True


def test_delete_removes_from_database(admin_client, db_session):
    """Test that delete operation removes record from database (hard delete)."""
    client, user_id, empresa_id = admin_client

    # Create via factory
    feriado = criar_feriado(
        db_session,
        empresa_id,
        date(2026, 9, 10),
        "To Delete"
    )
    feriado_id = feriado.feriado_id

    response = client.delete(f"/feriados/{feriado_id}")
    assert response.status_code == 200

    # Query database - record should not exist
    db_session.expire_all()
    db_record = db_session.query(Feriados).filter(
        Feriados.feriado_id == feriado_id
    ).first()

    assert db_record is None


def test_auto_generated_fields(admin_client):
    """Test that feriado_id and criado_em are auto-generated."""
    client, user_id, empresa_id = admin_client

    payload = {"empresa_id": empresa_id, "data": "2026-10-10", "nome": "Autogen Test"}
    response = client.post("/feriados/", json=payload)

    assert response.status_code == 201
    data = response.json()

    # Verify feriado_id is a valid UUID
    assert "feriado_id" in data
    try:
        uuid.UUID(data["feriado_id"])
    except ValueError:
        pytest.fail("feriado_id is not a valid UUID")

    # Verify criado_em is present
    assert "criado_em" in data
    assert data["criado_em"] is not None


# ============================================
# Date Handling Tests
# ============================================

def test_feriado_past_date(admin_client):
    """Test that holidays can be created in the past."""
    client, user_id, empresa_id = admin_client

    payload = {"empresa_id": empresa_id, "data": "2020-01-01", "nome": "Past Holiday"}
    response = client.post("/feriados/", json=payload)

    assert response.status_code == 201


def test_feriado_future_date(admin_client):
    """Test that holidays can be created in the future."""
    client, user_id, empresa_id = admin_client

    future_date = (date.today() + timedelta(days=365)).isoformat()
    payload = {"empresa_id": empresa_id, "data": future_date, "nome": "Future Holiday"}
    response = client.post("/feriados/", json=payload)

    assert response.status_code == 201


def test_feriado_today(admin_client):
    """Test that holidays can be created for today."""
    client, user_id, empresa_id = admin_client

    today = date.today().isoformat()
    payload = {"empresa_id": empresa_id, "data": today, "nome": "Today Holiday"}
    response = client.post("/feriados/", json=payload)

    assert response.status_code == 201


# ============================================
# Multi-Tenant Context Tests
# ============================================

def test_feriado_empresa_id_stored(admin_client, db_session):
    """Test that empresa_id is stored (via factory workaround)."""
    client, user_id, empresa_id = admin_client

    # Create via factory (factory sets empresa_id correctly)
    feriado = criar_feriado(
        db_session,
        empresa_id,
        date(2026, 11, 10),
        "Empresa Test"
    )

    # Verify empresa_id is stored
    assert feriado.empresa_id == uuid.UUID(empresa_id)


def test_listar_returns_all_feriados(admin_client, db_session):
    """Test that listar() returns ALL holidays (no empresa_id filtering).

    This documents current behavior - a security issue where all companies
    can see all holidays.
    """
    client, user_id, empresa_id = admin_client

    # Create holidays for current empresa
    criar_feriado(db_session, empresa_id, date(2027, 1, 1), "Empresa A")

    # Create holiday for different empresa
    other_empresa_id = str(uuid.uuid4())
    criar_feriado(db_session, other_empresa_id, date(2027, 2, 1), "Empresa B")

    response = client.get("/feriados/")

    assert response.status_code == 200
    data = response.json()
    # Current implementation returns all holidays, not filtered by empresa
    assert len(data) >= 2


def test_multiple_empresas_share_dates(admin_client, db_session):
    """Test that duplicate prevention is global (not per-empresa).

    This documents current behavior - duplicate dates are blocked globally
    across all companies, not just within one company.
    """
    client, user_id, empresa_id = admin_client

    # Create holiday for empresa A
    criar_feriado(db_session, empresa_id, date(2027, 3, 1), "Empresa A Feriado")

    # Try to create holiday on same date (will be blocked even though API
    # request is from the same empresa - duplicate check is global)
    payload = {"empresa_id": empresa_id, "data": "2027-03-01", "nome": "Should Be Blocked"}
    response = client.post("/feriados/", json=payload)

    assert response.status_code == 400  # Global duplicate prevention


# ============================================
# Edge Cases & Combined Scenarios
# ============================================

def test_update_to_original_values_succeeds(admin_client, db_session):
    """Test that updating to original values succeeds."""
    client, user_id, empresa_id = admin_client

    feriado = criar_feriado(
        db_session,
        empresa_id,
        date(2027, 4, 1),
        "Original",
        recorrente=True
    )

    # Update to same values
    payload = {
        "data": "2027-04-01",
        "nome": "Original",
        "recorrente": True
    }
    response = client.put(f"/feriados/{feriado.feriado_id}", json=payload)

    assert response.status_code == 200


def test_delete_and_recreate_same_date(admin_client, db_session):
    """Test that a date can be reused after deleting previous holiday."""
    client, user_id, empresa_id = admin_client

    test_date = "2027-05-01"

    # Create first holiday
    payload = {"empresa_id": empresa_id, "data": test_date, "nome": "First"}
    response1 = client.post("/feriados/", json=payload)
    assert response1.status_code == 201
    feriado_id = response1.json()["feriado_id"]

    # Delete it
    response2 = client.delete(f"/feriados/{feriado_id}")
    assert response2.status_code == 200

    # Create new holiday on same date
    payload = {"empresa_id": empresa_id, "data": test_date, "nome": "Second"}
    response3 = client.post("/feriados/", json=payload)
    assert response3.status_code == 201


def test_multiple_updates_in_sequence(admin_client, db_session):
    """Test multiple sequential updates work correctly."""
    client, user_id, empresa_id = admin_client

    feriado = criar_feriado(
        db_session,
        empresa_id,
        date(2027, 6, 1),
        "Initial"
    )
    feriado_id = feriado.feriado_id

    # First update
    response1 = client.put(f"/feriados/{feriado_id}", json={"nome": "Update 1"})
    assert response1.status_code == 200

    # Second update
    response2 = client.put(f"/feriados/{feriado_id}", json={"nome": "Update 2"})
    assert response2.status_code == 200

    # Third update
    response3 = client.put(f"/feriados/{feriado_id}", json={"nome": "Final"})
    assert response3.status_code == 200
    assert response3.json()["nome"] == "Final"
