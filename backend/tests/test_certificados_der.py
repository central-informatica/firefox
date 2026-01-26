"""
Tests for POST /certificados/der endpoint.

Tests:
- Access control (grupo membership)
- Access rules (day/time/holiday)
- Multiple certificates handling
- ID mapping (local ↔ cofre)

Note: The /der endpoint auto-discovers accessible certificates - no request body needed.
"""

import uuid
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.api.deps import check_auth_with_ip
from backend.app.db.session import get_db

from tests.factories.plano_factory import criar_plano
from tests.factories.grupo_factory import criar_grupo
from tests.factories.certificado_factory import criar_certificado
from tests.factories.grupo_certificado_factory import vincular_certificado_ao_grupo
from tests.factories.grupo_usuario_factory import adicionar_usuario_ao_grupo
from tests.factories.regra_acesso_factory import criar_regra_acesso
from tests.factories.feriado_factory import criar_feriado
from tests.factories.usuarios_ip_whitelist_factory import criar_usuarios_ip_whitelist


# ============================================
# HELPER FUNCTIONS
# ============================================

def _mock_user_data(user_id: str, org_id: str, ip: str = "127.0.0.1"):
    """Create mock user data dict as returned by auth service."""
    return {
        "id": user_id,
        "usuario_id": user_id,
        "organization_id": org_id,
        "is_admin": True,
        "email": "user@test.com",
        "ip_address": ip,
    }


def _janela_inclui_agora():
    """Create time window that includes current time."""
    now = datetime.now()
    ini = (now - timedelta(minutes=5)).strftime("%H:%M")
    fim = (now + timedelta(minutes=5)).strftime("%H:%M")
    return [{"inicio": ini, "fim": fim}]


def _janela_exclui_agora():
    """Create time window that excludes current time."""
    now = datetime.now()
    ini = (now - timedelta(hours=3)).strftime("%H:%M")
    fim = (now - timedelta(hours=2)).strftime("%H:%M")
    return [{"inicio": ini, "fim": fim}]


def _setup_completo(db, user_id, empresa_id):
    """
    Setup complete chain: plano -> grupo -> cert -> grupo_cert -> user.

    Returns:
        tuple: (plano, grupo, cert, grupo_cert)
    """
    plano = criar_plano(db, empresa_id)
    grupo = criar_grupo(db, empresa_id, plano.plano_id)
    cert = criar_certificado(db, empresa_id, user_id)

    # Set cofre_cert_id for the endpoint
    cert.cofre_cert_id = str(uuid.uuid4())
    db.commit()
    db.refresh(cert)

    grupo_cert = vincular_certificado_ao_grupo(db, empresa_id, grupo.grupo_id, cert.certificado_id)
    adicionar_usuario_ao_grupo(db, empresa_id, grupo.grupo_id, user_id)

    return plano, grupo, cert, grupo_cert


# ============================================
# FIXTURES
# ============================================

@pytest.fixture
def user_id():
    """Generate a test user ID."""
    return str(uuid.uuid4())


@pytest.fixture
def empresa_id():
    """Generate a test empresa ID."""
    return str(uuid.uuid4())


@pytest.fixture
def mock_cofre_der():
    """Mock cofre_client.get_certificates_der to avoid external calls."""
    with patch(
        "backend.app.api.routes.certificados.cofre_client.get_certificates_der",
        new_callable=AsyncMock
    ) as mock:
        # Default return value - will be customized per test
        mock.return_value = []
        yield mock


@pytest.fixture
def der_client(db_session, user_id, empresa_id, mock_cofre_der):
    """
    Create test client with auth dependency overridden.
    Also adds IP whitelist entry for the user.
    """
    # Add IP whitelist entry
    criar_usuarios_ip_whitelist(
        db_session,
        usuario_id=user_id,
        empresa_id=empresa_id,
        ip_address="127.0.0.1",
    )

    async def mock_auth():
        return _mock_user_data(user_id, empresa_id)

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[check_auth_with_ip] = mock_auth
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


# ============================================
# ACCESS CONTROL TESTS
# ============================================

def test_der_acesso_permitido(der_client, db_session, user_id, empresa_id, mock_cofre_der):
    """User with grupo access and valid time gets DER data."""
    plano, grupo, cert, grupo_cert = _setup_completo(db_session, user_id, empresa_id)

    criar_regra_acesso(
        db_session,
        empresa_id=empresa_id,
        grupo_id=grupo.grupo_id,
        tipo_dia="corridos",
        horarios=_janela_inclui_agora(),
    )

    # Mock Cofre response
    mock_cofre_der.return_value = [
        {"id": str(cert.cofre_cert_id), "label": "test.pfx", "cert_der_b64": "base64data"}
    ]

    resp = der_client.get("/certificados/der")

    assert resp.status_code == 200
    data = resp.json()
    assert len(data["certificates"]) == 1
    assert len(data["errors"]) == 0
    assert data["certificates"][0]["cert_der_b64"] == "base64data"


def test_der_sem_acesso_grupo(der_client, db_session, user_id, empresa_id, mock_cofre_der):
    """User not in any grupo gets empty response."""
    # Create cert with a DIFFERENT user (not the test user) in a different empresa
    another_user_id = str(uuid.uuid4())
    another_empresa_id = str(uuid.uuid4())

    plano = criar_plano(db_session, another_empresa_id)
    grupo = criar_grupo(db_session, another_empresa_id, plano.plano_id)
    cert = criar_certificado(db_session, another_empresa_id, another_user_id)
    cert.cofre_cert_id = str(uuid.uuid4())
    db_session.commit()

    vincular_certificado_ao_grupo(db_session, another_empresa_id, grupo.grupo_id, cert.certificado_id)
    # Note: test user (user_id) is NOT in this grupo and not in this empresa

    resp = der_client.get("/certificados/der")

    assert resp.status_code == 200
    data = resp.json()
    # User has no grupo membership, so no certs discovered
    assert len(data["certificates"]) == 0
    assert len(data["errors"]) == 0


def test_der_fora_horario(der_client, db_session, user_id, empresa_id, mock_cofre_der):
    """Request outside time window gets error."""
    plano, grupo, cert, grupo_cert = _setup_completo(db_session, user_id, empresa_id)

    criar_regra_acesso(
        db_session,
        empresa_id=empresa_id,
        grupo_id=grupo.grupo_id,
        tipo_dia="corridos",
        horarios=_janela_exclui_agora(),
    )

    resp = der_client.get("/certificados/der")

    assert resp.status_code == 200
    data = resp.json()
    assert len(data["certificates"]) == 0
    assert len(data["errors"]) == 1
    assert "fora do horario" in data["errors"][0]["reason"]


def test_der_feriado_bloqueia(der_client, db_session, user_id, empresa_id, mock_cofre_der):
    """Holiday with bloquear_em_feriado=True blocks access."""
    plano, grupo, cert, grupo_cert = _setup_completo(db_session, user_id, empresa_id)

    criar_regra_acesso(
        db_session,
        empresa_id=empresa_id,
        grupo_id=grupo.grupo_id,
        tipo_dia="corridos",
        horarios=_janela_inclui_agora(),
        bloquear_em_feriado=True,
    )

    # Create holiday for today
    hoje = datetime.now().date()
    criar_feriado(db_session, empresa_id, hoje, nome="Feriado Teste")

    resp = der_client.get("/certificados/der")

    assert resp.status_code == 200
    data = resp.json()
    assert len(data["certificates"]) == 0
    assert len(data["errors"]) == 1


# ============================================
# MULTIPLE CERTIFICATES TESTS
# ============================================

def test_der_multiplos_permitidos(der_client, db_session, user_id, empresa_id, mock_cofre_der):
    """Multiple accessible certs return all DER data."""
    plano = criar_plano(db_session, empresa_id)
    grupo = criar_grupo(db_session, empresa_id, plano.plano_id)

    # Create 2 certificates
    cert1 = criar_certificado(db_session, empresa_id, user_id, nome_arquivo="cert1.pfx")
    cert1.cofre_cert_id = str(uuid.uuid4())

    cert2 = criar_certificado(db_session, empresa_id, user_id, nome_arquivo="cert2.pfx")
    cert2.cofre_cert_id = str(uuid.uuid4())
    db_session.commit()

    vincular_certificado_ao_grupo(db_session, empresa_id, grupo.grupo_id, cert1.certificado_id)
    vincular_certificado_ao_grupo(db_session, empresa_id, grupo.grupo_id, cert2.certificado_id)
    adicionar_usuario_ao_grupo(db_session, empresa_id, grupo.grupo_id, user_id)

    criar_regra_acesso(
        db_session,
        empresa_id=empresa_id,
        grupo_id=grupo.grupo_id,
        tipo_dia="corridos",
        horarios=_janela_inclui_agora(),
    )

    # Mock Cofre response for both
    mock_cofre_der.return_value = [
        {"id": str(cert1.cofre_cert_id), "label": "cert1.pfx", "cert_der_b64": "data1"},
        {"id": str(cert2.cofre_cert_id), "label": "cert2.pfx", "cert_der_b64": "data2"},
    ]

    resp = der_client.get("/certificados/der")

    assert resp.status_code == 200
    data = resp.json()
    assert len(data["certificates"]) == 2
    assert len(data["errors"]) == 0


def test_der_parcial_acesso(der_client, db_session, user_id, empresa_id, mock_cofre_der):
    """Mix of allowed/denied certs returns partial results (based on access rules)."""
    plano = criar_plano(db_session, empresa_id)

    # Grupo 1: user has access, valid time window
    grupo1 = criar_grupo(db_session, empresa_id, plano.plano_id, nome="Grupo1")
    cert1 = criar_certificado(db_session, empresa_id, user_id, nome_arquivo="cert1.pfx")
    cert1.cofre_cert_id = str(uuid.uuid4())
    db_session.commit()

    vincular_certificado_ao_grupo(db_session, empresa_id, grupo1.grupo_id, cert1.certificado_id)
    adicionar_usuario_ao_grupo(db_session, empresa_id, grupo1.grupo_id, user_id)

    criar_regra_acesso(
        db_session,
        empresa_id=empresa_id,
        grupo_id=grupo1.grupo_id,
        tipo_dia="corridos",
        horarios=_janela_inclui_agora(),
    )

    # Grupo 2: user has access but INVALID time window
    grupo2 = criar_grupo(db_session, empresa_id, plano.plano_id, nome="Grupo2")
    cert2 = criar_certificado(db_session, empresa_id, user_id, nome_arquivo="cert2.pfx")
    cert2.cofre_cert_id = str(uuid.uuid4())
    db_session.commit()

    vincular_certificado_ao_grupo(db_session, empresa_id, grupo2.grupo_id, cert2.certificado_id)
    adicionar_usuario_ao_grupo(db_session, empresa_id, grupo2.grupo_id, user_id)

    criar_regra_acesso(
        db_session,
        empresa_id=empresa_id,
        grupo_id=grupo2.grupo_id,
        tipo_dia="corridos",
        horarios=_janela_exclui_agora(),  # Invalid time window
    )

    # Mock Cofre response for cert1 only
    mock_cofre_der.return_value = [
        {"id": str(cert1.cofre_cert_id), "label": "cert1.pfx", "cert_der_b64": "data1"},
    ]

    resp = der_client.get("/certificados/der")

    assert resp.status_code == 200
    data = resp.json()
    assert len(data["certificates"]) == 1
    assert len(data["errors"]) == 1  # cert2 denied due to time
    assert data["certificates"][0]["id"] == str(cert1.certificado_id)


def test_der_todos_negados(der_client, db_session, user_id, empresa_id, mock_cofre_der):
    """All certs denied returns empty certificates with errors."""
    plano = criar_plano(db_session, empresa_id)
    grupo = criar_grupo(db_session, empresa_id, plano.plano_id)

    cert = criar_certificado(db_session, empresa_id, user_id)
    cert.cofre_cert_id = str(uuid.uuid4())
    db_session.commit()

    vincular_certificado_ao_grupo(db_session, empresa_id, grupo.grupo_id, cert.certificado_id)
    adicionar_usuario_ao_grupo(db_session, empresa_id, grupo.grupo_id, user_id)
    # No access rules created

    resp = der_client.get("/certificados/der")

    assert resp.status_code == 200
    data = resp.json()
    assert len(data["certificates"]) == 0
    assert len(data["errors"]) == 1
    assert "nenhuma regra de acesso" in data["errors"][0]["reason"]


# ============================================
# EDGE CASES
# ============================================

def test_der_sem_certificados(der_client, db_session, user_id, empresa_id, mock_cofre_der):
    """User with no accessible certificates gets empty response."""
    resp = der_client.get("/certificados/der")

    assert resp.status_code == 200
    data = resp.json()
    assert len(data["certificates"]) == 0
    assert len(data["errors"]) == 0


def test_der_certificado_sem_cofre_id_nao_aparece(der_client, db_session, user_id, empresa_id, mock_cofre_der):
    """Cert without cofre_cert_id is filtered out in discovery."""
    plano = criar_plano(db_session, empresa_id)
    grupo = criar_grupo(db_session, empresa_id, plano.plano_id)

    cert = criar_certificado(db_session, empresa_id, user_id)
    # Note: cofre_cert_id is NOT set (None)
    db_session.commit()

    vincular_certificado_ao_grupo(db_session, empresa_id, grupo.grupo_id, cert.certificado_id)
    adicionar_usuario_ao_grupo(db_session, empresa_id, grupo.grupo_id, user_id)

    criar_regra_acesso(
        db_session,
        empresa_id=empresa_id,
        grupo_id=grupo.grupo_id,
        tipo_dia="corridos",
        horarios=_janela_inclui_agora(),
    )

    resp = der_client.get("/certificados/der")

    assert resp.status_code == 200
    data = resp.json()
    # Cert without cofre_cert_id is not discovered
    assert len(data["certificates"]) == 0
    assert len(data["errors"]) == 0


def test_der_certificado_deletado_nao_aparece(der_client, db_session, user_id, empresa_id, mock_cofre_der):
    """Soft-deleted certificate is not discovered."""
    plano, grupo, cert, grupo_cert = _setup_completo(db_session, user_id, empresa_id)

    criar_regra_acesso(
        db_session,
        empresa_id=empresa_id,
        grupo_id=grupo.grupo_id,
        tipo_dia="corridos",
        horarios=_janela_inclui_agora(),
    )

    # Soft delete the certificate
    cert.deleted_at = datetime.now()
    db_session.commit()

    resp = der_client.get("/certificados/der")

    assert resp.status_code == 200
    data = resp.json()
    # Deleted cert is not discovered
    assert len(data["certificates"]) == 0
    assert len(data["errors"]) == 0


# ============================================
# ID MAPPING TEST
# ============================================

def test_der_retorna_id_local(der_client, db_session, user_id, empresa_id, mock_cofre_der):
    """Response maps Cofre ID back to local certificado_id."""
    plano, grupo, cert, grupo_cert = _setup_completo(db_session, user_id, empresa_id)

    criar_regra_acesso(
        db_session,
        empresa_id=empresa_id,
        grupo_id=grupo.grupo_id,
        tipo_dia="corridos",
        horarios=_janela_inclui_agora(),
    )

    local_id = str(cert.certificado_id)
    cofre_id = str(cert.cofre_cert_id)

    # Mock Cofre response with cofre_cert_id
    mock_cofre_der.return_value = [
        {"id": cofre_id, "label": "test.pfx", "cert_der_b64": "base64data"}
    ]

    resp = der_client.get("/certificados/der")

    assert resp.status_code == 200
    data = resp.json()
    assert len(data["certificates"]) == 1

    # Verify response uses LOCAL ID, not Cofre ID
    assert data["certificates"][0]["id"] == local_id
    assert data["certificates"][0]["id"] != cofre_id
