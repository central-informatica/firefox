"""Tests for UsuariosIpWhitelist API endpoints."""

import uuid
from backend.app.main import app
from backend.app.api.deps import check_auth_with_ip, check_auth
from backend.app.db.models import UsuariosIpWhitelist
from tests.factories.usuarios_ip_whitelist_factory import criar_usuarios_ip_whitelist


# ---------------------------------------------------------------------------
# Helper: mock check_auth_with_ip
# ---------------------------------------------------------------------------
def _mock_admin_user(user_id=None, org_id=None, ip_address="127.0.0.1"):
    """Return mock check_auth_with_ip for admin user."""
    async def mock():
        return {
            "id": user_id or str(uuid.uuid4()),
            "is_admin": True,
            "organization_id": org_id or str(uuid.uuid4()),
            "email": "admin@test.com",
            "ip_address": ip_address,
        }
    return mock


def _mock_non_admin_user(user_id=None, org_id=None, ip_address="127.0.0.1"):
    """Return mock check_auth_with_ip for non-admin user."""
    async def mock():
        return {
            "id": user_id or str(uuid.uuid4()),
            "is_admin": False,
            "organization_id": org_id or str(uuid.uuid4()),
            "email": "user@test.com",
            "ip_address": ip_address,
        }
    return mock


# ---------------------------------------------------------------------------
# GET /usuarios-ip-whitelist/empresa/{empresa_id}
# ---------------------------------------------------------------------------
def test_listar_por_empresa_admin_success(client, db_session):
    """Admin can list all entries for an empresa."""
    user_id = str(uuid.uuid4())
    empresa_id = str(uuid.uuid4())

    criar_usuarios_ip_whitelist(db_session, user_id, empresa_id, "10.0.0.1")
    criar_usuarios_ip_whitelist(db_session, user_id, empresa_id, "10.0.0.2")

    app.dependency_overrides[check_auth_with_ip] = _mock_admin_user(user_id, empresa_id)

    response = client.get(f"/usuarios-ip-whitelist/empresa/{empresa_id}")

    app.dependency_overrides.pop(check_auth_with_ip, None)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_listar_por_empresa_non_admin_forbidden(client, db_session):
    """Non-admin gets 403."""
    empresa_id = str(uuid.uuid4())

    app.dependency_overrides[check_auth_with_ip] = _mock_non_admin_user()

    response = client.get(f"/usuarios-ip-whitelist/empresa/{empresa_id}")

    app.dependency_overrides.pop(check_auth_with_ip, None)

    assert response.status_code == 403


def test_listar_por_empresa_unauthenticated(client):
    """Unauthenticated request gets 401."""
    empresa_id = str(uuid.uuid4())

    response = client.get(f"/usuarios-ip-whitelist/empresa/{empresa_id}")

    assert response.status_code == 401


def test_listar_por_empresa_excludes_deleted(client, db_session):
    """Listing excludes soft-deleted entries."""
    user_id = str(uuid.uuid4())
    empresa_id = str(uuid.uuid4())

    entry1 = criar_usuarios_ip_whitelist(db_session, user_id, empresa_id, "10.0.0.1")
    entry2 = criar_usuarios_ip_whitelist(db_session, user_id, empresa_id, "10.0.0.2")

    # Soft delete entry2
    import datetime
    entry2.deleted_at = datetime.datetime.now(datetime.timezone.utc)
    db_session.commit()

    app.dependency_overrides[check_auth_with_ip] = _mock_admin_user(user_id, empresa_id)

    response = client.get(f"/usuarios-ip-whitelist/empresa/{empresa_id}")

    app.dependency_overrides.pop(check_auth_with_ip, None)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["ip_address"] == "203.0.113.1"


# ---------------------------------------------------------------------------
# GET /usuarios-ip-whitelist/usuario/{usuario_id}
# ---------------------------------------------------------------------------
def test_listar_por_usuario_success(client, db_session):
    """List entries for a specific user."""
    user_id = str(uuid.uuid4())
    empresa_id = str(uuid.uuid4())

    criar_usuarios_ip_whitelist(db_session, user_id, empresa_id, "10.0.0.1")

    app.dependency_overrides[check_auth_with_ip] = _mock_admin_user(user_id, empresa_id)

    response = client.get(f"/usuarios-ip-whitelist/usuario/{user_id}")

    app.dependency_overrides.pop(check_auth_with_ip, None)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1


# ---------------------------------------------------------------------------
# GET /usuarios-ip-whitelist/{whitelist_id}
# ---------------------------------------------------------------------------
def test_obter_entry_success(client, db_session):
    """Get specific entry by ID."""
    user_id = str(uuid.uuid4())
    empresa_id = str(uuid.uuid4())

    entry = criar_usuarios_ip_whitelist(db_session, user_id, empresa_id, "10.0.0.1")

    app.dependency_overrides[check_auth_with_ip] = _mock_admin_user(user_id, empresa_id)

    response = client.get(f"/usuarios-ip-whitelist/{entry.whitelist_id}")

    app.dependency_overrides.pop(check_auth_with_ip, None)

    assert response.status_code == 200
    data = response.json()
    assert data["ip_address"] == "203.0.113.1"


def test_obter_deleted_entry_returns_404(client, db_session):
    """Getting a soft-deleted entry returns 404."""
    user_id = str(uuid.uuid4())
    empresa_id = str(uuid.uuid4())

    entry = criar_usuarios_ip_whitelist(db_session, user_id, empresa_id, "10.0.0.1")

    # Soft delete
    import datetime
    entry.deleted_at = datetime.datetime.now(datetime.timezone.utc)
    db_session.commit()

    app.dependency_overrides[check_auth_with_ip] = _mock_admin_user(user_id, empresa_id)

    response = client.get(f"/usuarios-ip-whitelist/{entry.whitelist_id}")

    app.dependency_overrides.pop(check_auth_with_ip, None)

    assert response.status_code == 404


def test_obter_nonexistent_returns_404(client, db_session):
    """Getting nonexistent entry returns 404."""
    fake_id = str(uuid.uuid4())

    app.dependency_overrides[check_auth_with_ip] = _mock_admin_user()

    response = client.get(f"/usuarios-ip-whitelist/{fake_id}")

    app.dependency_overrides.pop(check_auth_with_ip, None)

    assert response.status_code == 404


# ---------------------------------------------------------------------------
# POST /usuarios-ip-whitelist/
# ---------------------------------------------------------------------------
def test_criar_admin_success(client, db_session):
    """Admin can create entry."""
    user_id = str(uuid.uuid4())
    empresa_id = str(uuid.uuid4())

    app.dependency_overrides[check_auth] = _mock_admin_user(user_id, empresa_id)

    payload = {
        "usuario_id": user_id,
        "empresa_id": empresa_id,
        "ip_address": "203.0.113.50",
        "descricao": "Office IP",
    }

    response = client.post("/usuarios-ip-whitelist/", json=payload)

    app.dependency_overrides.pop(check_auth, None)

    assert response.status_code == 201
    data = response.json()
    assert data["ip_address"] == "203.0.113.50"
    assert data["descricao"] == "Office IP"


def test_criar_non_admin_forbidden(client, db_session):
    """Non-admin gets 403."""
    user_id = str(uuid.uuid4())
    empresa_id = str(uuid.uuid4())

    app.dependency_overrides[check_auth] = _mock_non_admin_user(user_id, empresa_id)

    payload = {
        "usuario_id": user_id,
        "empresa_id": empresa_id,
        "ip_address": "203.0.113.50",
    }

    response = client.post("/usuarios-ip-whitelist/", json=payload)

    app.dependency_overrides.pop(check_auth, None)

    assert response.status_code == 403


def test_criar_duplicate_ip_returns_409(client, db_session):
    """Creating duplicate user+empresa+IP returns 409."""
    user_id = str(uuid.uuid4())
    empresa_id = str(uuid.uuid4())

    criar_usuarios_ip_whitelist(db_session, user_id, empresa_id, "192.168.1.50")

    app.dependency_overrides[check_auth] = _mock_admin_user(user_id, empresa_id)

    payload = {
        "usuario_id": user_id,
        "empresa_id": empresa_id,
        "ip_address": "203.0.113.50",
    }

    response = client.post("/usuarios-ip-whitelist/", json=payload)

    app.dependency_overrides.pop(check_auth, None)

    assert response.status_code == 409


def test_criar_invalid_ip_returns_422(client, db_session):
    """Invalid IP address returns 422."""
    user_id = str(uuid.uuid4())
    empresa_id = str(uuid.uuid4())

    app.dependency_overrides[check_auth] = _mock_admin_user(user_id, empresa_id)

    payload = {
        "usuario_id": user_id,
        "empresa_id": empresa_id,
        "ip_address": "not-an-ip",
    }

    response = client.post("/usuarios-ip-whitelist/", json=payload)

    app.dependency_overrides.pop(check_auth, None)

    assert response.status_code == 422


def test_criar_ipv6_success(client, db_session):
    """IPv6 addresses are accepted."""
    user_id = str(uuid.uuid4())
    empresa_id = str(uuid.uuid4())

    app.dependency_overrides[check_auth] = _mock_admin_user(user_id, empresa_id)

    payload = {
        "usuario_id": user_id,
        "empresa_id": empresa_id,
        "ip_address": "2001:db8::1",
    }

    response = client.post("/usuarios-ip-whitelist/", json=payload)

    app.dependency_overrides.pop(check_auth, None)

    assert response.status_code == 201
    assert response.json()["ip_address"] == "2001:db8::1"


# ---------------------------------------------------------------------------
# PUT /usuarios-ip-whitelist/{whitelist_id}
# ---------------------------------------------------------------------------
def test_atualizar_admin_success(client, db_session):
    """Admin can update entry."""
    user_id = str(uuid.uuid4())
    empresa_id = str(uuid.uuid4())

    entry = criar_usuarios_ip_whitelist(db_session, user_id, empresa_id, "10.0.0.1")

    app.dependency_overrides[check_auth_with_ip] = _mock_admin_user(user_id, empresa_id)

    payload = {"ip_address": "203.0.113.99", "descricao": "Updated"}

    response = client.put(f"/usuarios-ip-whitelist/{entry.whitelist_id}", json=payload)

    app.dependency_overrides.pop(check_auth_with_ip, None)

    assert response.status_code == 200
    data = response.json()
    assert data["ip_address"] == "203.0.113.99"
    assert data["descricao"] == "Updated"


def test_atualizar_non_admin_forbidden(client, db_session):
    """Non-admin gets 403."""
    user_id = str(uuid.uuid4())
    empresa_id = str(uuid.uuid4())

    entry = criar_usuarios_ip_whitelist(db_session, user_id, empresa_id, "10.0.0.1")

    app.dependency_overrides[check_auth_with_ip] = _mock_non_admin_user(user_id, empresa_id)

    payload = {"ip_address": "203.0.113.99"}

    response = client.put(f"/usuarios-ip-whitelist/{entry.whitelist_id}", json=payload)

    app.dependency_overrides.pop(check_auth_with_ip, None)

    assert response.status_code == 403


def test_atualizar_to_duplicate_ip_returns_409(client, db_session):
    """Updating to duplicate IP returns 409."""
    user_id = str(uuid.uuid4())
    empresa_id = str(uuid.uuid4())

    criar_usuarios_ip_whitelist(db_session, user_id, empresa_id, "10.0.0.1")
    entry2 = criar_usuarios_ip_whitelist(db_session, user_id, empresa_id, "10.0.0.2")

    app.dependency_overrides[check_auth_with_ip] = _mock_admin_user(user_id, empresa_id)

    payload = {"ip_address": "203.0.113.1"}

    response = client.put(f"/usuarios-ip-whitelist/{entry2.whitelist_id}", json=payload)

    app.dependency_overrides.pop(check_auth_with_ip, None)

    assert response.status_code == 409


# ---------------------------------------------------------------------------
# DELETE /usuarios-ip-whitelist/{whitelist_id}
# ---------------------------------------------------------------------------
def test_deletar_admin_success(client, db_session):
    """Admin can soft delete entry."""
    user_id = str(uuid.uuid4())
    empresa_id = str(uuid.uuid4())

    entry = criar_usuarios_ip_whitelist(db_session, user_id, empresa_id, "10.0.0.1")

    app.dependency_overrides[check_auth_with_ip] = _mock_admin_user(user_id, empresa_id)

    response = client.delete(f"/usuarios-ip-whitelist/{entry.whitelist_id}")

    app.dependency_overrides.pop(check_auth_with_ip, None)

    assert response.status_code == 200
    assert response.json()["status"] == "deleted"

    # Verify soft delete
    db_session.refresh(entry)
    assert entry.deleted_at is not None
    assert str(entry.deleted_by) == user_id


def test_deletar_non_admin_forbidden(client, db_session):
    """Non-admin gets 403."""
    user_id = str(uuid.uuid4())
    empresa_id = str(uuid.uuid4())

    entry = criar_usuarios_ip_whitelist(db_session, user_id, empresa_id, "10.0.0.1")

    app.dependency_overrides[check_auth_with_ip] = _mock_non_admin_user(user_id, empresa_id)

    response = client.delete(f"/usuarios-ip-whitelist/{entry.whitelist_id}")

    app.dependency_overrides.pop(check_auth_with_ip, None)

    assert response.status_code == 403


# ---------------------------------------------------------------------------
# DELETE /usuarios-ip-whitelist/usuario/{usuario_id}
# ---------------------------------------------------------------------------
def test_deletar_todos_por_usuario_success(client, db_session):
    """Admin can delete all entries for a user."""
    user_id = str(uuid.uuid4())
    empresa_id = str(uuid.uuid4())

    criar_usuarios_ip_whitelist(db_session, user_id, empresa_id, "10.0.0.1")
    criar_usuarios_ip_whitelist(db_session, user_id, empresa_id, "10.0.0.2")

    app.dependency_overrides[check_auth_with_ip] = _mock_admin_user(user_id, empresa_id)

    response = client.delete(f"/usuarios-ip-whitelist/usuario/{user_id}")

    app.dependency_overrides.pop(check_auth_with_ip, None)

    assert response.status_code == 200
    assert response.json()["deleted_count"] == 2


def test_deletar_todos_por_usuario_non_admin_forbidden(client, db_session):
    """Non-admin gets 403."""
    user_id = str(uuid.uuid4())
    empresa_id = str(uuid.uuid4())

    app.dependency_overrides[check_auth_with_ip] = _mock_non_admin_user(user_id, empresa_id)

    response = client.delete(f"/usuarios-ip-whitelist/usuario/{user_id}")

    app.dependency_overrides.pop(check_auth_with_ip, None)

    assert response.status_code == 403
