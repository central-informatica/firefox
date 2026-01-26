"""
Tests for certificate signing access control.

Tests:
- Access rules (tipo_dia, horarios)
- Holiday blocking (bloquear_em_feriado)
- URL-based access control (grupos_certificados_urls)
"""

import base64
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
from tests.factories.global_urls_factory import criar_global_url
from tests.factories.grupos_certificados_urls_factory import criar_grupos_certificados_urls
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
    # Window in the past
    ini = (now - timedelta(hours=3)).strftime("%H:%M")
    fim = (now - timedelta(hours=2)).strftime("%H:%M")
    return [{"inicio": ini, "fim": fim}]


def _iso_weekday():
    """Get current weekday (1=Monday, 7=Sunday)."""
    return datetime.now().isoweekday()


def _setup_completo(db, user_id, empresa_id):
    """
    Setup complete chain: plano -> grupo -> cert -> grupo_cert -> user.

    Returns:
        tuple: (plano, grupo, cert, grupo_cert)
    """
    plano = criar_plano(db, empresa_id)
    grupo = criar_grupo(db, empresa_id, plano.plano_id)
    cert = criar_certificado(db, empresa_id, user_id)

    # Set cofre_cert_id for signing endpoint
    cert.cofre_cert_id = str(uuid.uuid4())
    db.commit()
    db.refresh(cert)

    grupo_cert = vincular_certificado_ao_grupo(db, empresa_id, grupo.grupo_id, cert.certificado_id)
    adicionar_usuario_ao_grupo(db, empresa_id, grupo.grupo_id, user_id)

    return plano, grupo, cert, grupo_cert


def _setup_url_permitida(db, empresa_id, grupo_cert_id, url="https://example.com"):
    """Setup allowed URL for grupo-certificado."""
    global_url = criar_global_url(db, empresa_id, url)
    criar_grupos_certificados_urls(db, grupo_cert_id, global_url.global_urls_id, empresa_id)
    return global_url


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
def mock_cofre_sign():
    """Mock cofre_client.sign_data to avoid external calls."""
    with patch("backend.app.api.routes.certificados.cofre_client.sign_data", new_callable=AsyncMock) as mock:
        mock.return_value = base64.b64encode(b"mocked_signature").decode()
        yield mock


@pytest.fixture
def signing_client(db_session, user_id, empresa_id, mock_cofre_sign):
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
# ACCESS RULES TESTS - TIPO_DIA
# ============================================

def test_assinar_tipo_dia_corridos_permite(signing_client, db_session, user_id, empresa_id):
    """tipo_dia=corridos should allow any day."""
    plano, grupo, cert, grupo_cert = _setup_completo(db_session, user_id, empresa_id)

    # Create access rule with corridos
    criar_regra_acesso(
        db_session,
        empresa_id=empresa_id,
        grupo_id=grupo.grupo_id,
        tipo_dia="corridos",
        horarios=_janela_inclui_agora(),
    )

    # Setup allowed URL
    _setup_url_permitida(db_session, empresa_id, grupo_cert.grupo_cert_id)

    # Attempt to sign
    resp = signing_client.post(
        f"/certificados/{cert.certificado_id}/assinar",
        json={"data": base64.b64encode(b"test data").decode(), "url": "https://example.com/path"}
    )

    assert resp.status_code == 200
    assert "signature" in resp.json()


def test_assinar_tipo_dia_uteis_permite_dia_util(signing_client, db_session, user_id, empresa_id):
    """tipo_dia=uteis should allow Monday-Friday."""
    plano, grupo, cert, grupo_cert = _setup_completo(db_session, user_id, empresa_id)

    criar_regra_acesso(
        db_session,
        empresa_id=empresa_id,
        grupo_id=grupo.grupo_id,
        tipo_dia="uteis",
        horarios=_janela_inclui_agora(),
    )

    _setup_url_permitida(db_session, empresa_id, grupo_cert.grupo_cert_id)

    resp = signing_client.post(
        f"/certificados/{cert.certificado_id}/assinar",
        json={"data": base64.b64encode(b"test data").decode(), "url": "https://example.com"}
    )

    weekday = _iso_weekday()
    if weekday <= 5:  # Monday-Friday
        assert resp.status_code == 200
    else:  # Saturday-Sunday
        assert resp.status_code == 403


def test_assinar_tipo_dia_especificos_permite_dia_listado(signing_client, db_session, user_id, empresa_id):
    """tipo_dia=especificos should allow days in dias_especificos."""
    plano, grupo, cert, grupo_cert = _setup_completo(db_session, user_id, empresa_id)

    hoje = _iso_weekday()

    criar_regra_acesso(
        db_session,
        empresa_id=empresa_id,
        grupo_id=grupo.grupo_id,
        tipo_dia="especificos",
        dias_especificos=[hoje],  # Today is allowed
        horarios=_janela_inclui_agora(),
    )

    _setup_url_permitida(db_session, empresa_id, grupo_cert.grupo_cert_id)

    resp = signing_client.post(
        f"/certificados/{cert.certificado_id}/assinar",
        json={"data": base64.b64encode(b"test data").decode(), "url": "https://example.com"}
    )

    assert resp.status_code == 200


def test_assinar_tipo_dia_especificos_bloqueia_dia_nao_listado(signing_client, db_session, user_id, empresa_id):
    """tipo_dia=especificos should block days not in dias_especificos."""
    plano, grupo, cert, grupo_cert = _setup_completo(db_session, user_id, empresa_id)

    hoje = _iso_weekday()
    outro_dia = 1 if hoje != 1 else 2

    criar_regra_acesso(
        db_session,
        empresa_id=empresa_id,
        grupo_id=grupo.grupo_id,
        tipo_dia="especificos",
        dias_especificos=[outro_dia],  # Today is NOT allowed
        horarios=_janela_inclui_agora(),
    )

    _setup_url_permitida(db_session, empresa_id, grupo_cert.grupo_cert_id)

    resp = signing_client.post(
        f"/certificados/{cert.certificado_id}/assinar",
        json={"data": base64.b64encode(b"test data").decode(), "url": "https://example.com"}
    )

    assert resp.status_code == 403
    assert "fora do horario ou dia permitido" in resp.json()["detail"]


# ============================================
# ACCESS RULES TESTS - HORARIOS
# ============================================

def test_assinar_dentro_do_horario_permite(signing_client, db_session, user_id, empresa_id):
    """Signing within allowed time window should succeed."""
    plano, grupo, cert, grupo_cert = _setup_completo(db_session, user_id, empresa_id)

    criar_regra_acesso(
        db_session,
        empresa_id=empresa_id,
        grupo_id=grupo.grupo_id,
        tipo_dia="corridos",
        horarios=_janela_inclui_agora(),
    )

    _setup_url_permitida(db_session, empresa_id, grupo_cert.grupo_cert_id)

    resp = signing_client.post(
        f"/certificados/{cert.certificado_id}/assinar",
        json={"data": base64.b64encode(b"test data").decode(), "url": "https://example.com"}
    )

    assert resp.status_code == 200


def test_assinar_fora_do_horario_bloqueia(signing_client, db_session, user_id, empresa_id):
    """Signing outside allowed time window should fail."""
    plano, grupo, cert, grupo_cert = _setup_completo(db_session, user_id, empresa_id)

    criar_regra_acesso(
        db_session,
        empresa_id=empresa_id,
        grupo_id=grupo.grupo_id,
        tipo_dia="corridos",
        horarios=_janela_exclui_agora(),  # Time window excludes now
    )

    _setup_url_permitida(db_session, empresa_id, grupo_cert.grupo_cert_id)

    resp = signing_client.post(
        f"/certificados/{cert.certificado_id}/assinar",
        json={"data": base64.b64encode(b"test data").decode(), "url": "https://example.com"}
    )

    assert resp.status_code == 403
    assert "fora do horario ou dia permitido" in resp.json()["detail"]


def test_assinar_multiplas_janelas_horario(signing_client, db_session, user_id, empresa_id):
    """Test with multiple time windows - one includes now."""
    plano, grupo, cert, grupo_cert = _setup_completo(db_session, user_id, empresa_id)

    # Multiple windows: one excludes, one includes
    horarios = _janela_exclui_agora() + _janela_inclui_agora()

    criar_regra_acesso(
        db_session,
        empresa_id=empresa_id,
        grupo_id=grupo.grupo_id,
        tipo_dia="corridos",
        horarios=horarios,
    )

    _setup_url_permitida(db_session, empresa_id, grupo_cert.grupo_cert_id)

    resp = signing_client.post(
        f"/certificados/{cert.certificado_id}/assinar",
        json={"data": base64.b64encode(b"test data").decode(), "url": "https://example.com"}
    )

    assert resp.status_code == 200


# ============================================
# HOLIDAY BLOCKING TESTS
# ============================================

def test_assinar_feriado_com_bloquear_em_feriado_true(signing_client, db_session, user_id, empresa_id):
    """Signing on holiday with bloquear_em_feriado=True should fail."""
    plano, grupo, cert, grupo_cert = _setup_completo(db_session, user_id, empresa_id)

    # Rule allows today but blocks holidays
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

    _setup_url_permitida(db_session, empresa_id, grupo_cert.grupo_cert_id)

    resp = signing_client.post(
        f"/certificados/{cert.certificado_id}/assinar",
        json={"data": base64.b64encode(b"test data").decode(), "url": "https://example.com"}
    )

    assert resp.status_code == 403


def test_assinar_feriado_com_bloquear_em_feriado_false(signing_client, db_session, user_id, empresa_id):
    """Signing on holiday with bloquear_em_feriado=False should succeed."""
    plano, grupo, cert, grupo_cert = _setup_completo(db_session, user_id, empresa_id)

    # Rule allows today and doesn't block holidays
    criar_regra_acesso(
        db_session,
        empresa_id=empresa_id,
        grupo_id=grupo.grupo_id,
        tipo_dia="corridos",
        horarios=_janela_inclui_agora(),
        bloquear_em_feriado=False,  # Default, but explicit
    )

    # Create holiday for today
    hoje = datetime.now().date()
    criar_feriado(db_session, empresa_id, hoje, nome="Feriado Teste")

    _setup_url_permitida(db_session, empresa_id, grupo_cert.grupo_cert_id)

    resp = signing_client.post(
        f"/certificados/{cert.certificado_id}/assinar",
        json={"data": base64.b64encode(b"test data").decode(), "url": "https://example.com"}
    )

    assert resp.status_code == 200


def test_assinar_feriado_recorrente_bloqueia(signing_client, db_session, user_id, empresa_id):
    """Recurrent holiday (same month/day) should block."""
    plano, grupo, cert, grupo_cert = _setup_completo(db_session, user_id, empresa_id)

    criar_regra_acesso(
        db_session,
        empresa_id=empresa_id,
        grupo_id=grupo.grupo_id,
        tipo_dia="corridos",
        horarios=_janela_inclui_agora(),
        bloquear_em_feriado=True,
    )

    # Create recurrent holiday for today's month/day but different year
    hoje = datetime.now().date()
    feriado_data = hoje.replace(year=2020)  # Different year
    criar_feriado(db_session, empresa_id, feriado_data, nome="Feriado Recorrente", recorrente=True)

    _setup_url_permitida(db_session, empresa_id, grupo_cert.grupo_cert_id)

    resp = signing_client.post(
        f"/certificados/{cert.certificado_id}/assinar",
        json={"data": base64.b64encode(b"test data").decode(), "url": "https://example.com"}
    )

    assert resp.status_code == 403


def test_assinar_dia_normal_com_regra_feriado_permite(signing_client, db_session, user_id, empresa_id):
    """Normal day should allow even with bloquear_em_feriado=True."""
    plano, grupo, cert, grupo_cert = _setup_completo(db_session, user_id, empresa_id)

    criar_regra_acesso(
        db_session,
        empresa_id=empresa_id,
        grupo_id=grupo.grupo_id,
        tipo_dia="corridos",
        horarios=_janela_inclui_agora(),
        bloquear_em_feriado=True,  # Would block if holiday, but no holiday
    )

    # No holiday created for today

    _setup_url_permitida(db_session, empresa_id, grupo_cert.grupo_cert_id)

    resp = signing_client.post(
        f"/certificados/{cert.certificado_id}/assinar",
        json={"data": base64.b64encode(b"test data").decode(), "url": "https://example.com"}
    )

    assert resp.status_code == 200


# ============================================
# NO RULES TESTS
# ============================================

def test_assinar_sem_regras_acesso_bloqueia(signing_client, db_session, user_id, empresa_id):
    """Signing without any access rules should fail with descriptive message."""
    plano, grupo, cert, grupo_cert = _setup_completo(db_session, user_id, empresa_id)

    # No rules created

    _setup_url_permitida(db_session, empresa_id, grupo_cert.grupo_cert_id)

    resp = signing_client.post(
        f"/certificados/{cert.certificado_id}/assinar",
        json={"data": base64.b64encode(b"test data").decode(), "url": "https://example.com"}
    )

    assert resp.status_code == 403
    assert "nenhuma regra de acesso" in resp.json()["detail"]


# ============================================
# URL-BASED ACCESS TESTS
# ============================================

def test_assinar_url_permitida_sucesso(signing_client, db_session, user_id, empresa_id):
    """Signing with allowed HTTPS URL should succeed."""
    plano, grupo, cert, grupo_cert = _setup_completo(db_session, user_id, empresa_id)

    criar_regra_acesso(
        db_session,
        empresa_id=empresa_id,
        grupo_id=grupo.grupo_id,
        tipo_dia="corridos",
        horarios=_janela_inclui_agora(),
    )

    # Setup allowed URL
    _setup_url_permitida(db_session, empresa_id, grupo_cert.grupo_cert_id, "https://allowed.com")

    resp = signing_client.post(
        f"/certificados/{cert.certificado_id}/assinar",
        json={"data": base64.b64encode(b"test data").decode(), "url": "https://allowed.com/some/path"}
    )

    assert resp.status_code == 200


def test_assinar_url_nao_permitida_bloqueia(signing_client, db_session, user_id, empresa_id):
    """Signing with URL not in allowed list should fail."""
    plano, grupo, cert, grupo_cert = _setup_completo(db_session, user_id, empresa_id)

    criar_regra_acesso(
        db_session,
        empresa_id=empresa_id,
        grupo_id=grupo.grupo_id,
        tipo_dia="corridos",
        horarios=_janela_inclui_agora(),
    )

    # Setup allowed URL for a different domain
    _setup_url_permitida(db_session, empresa_id, grupo_cert.grupo_cert_id, "https://allowed.com")

    resp = signing_client.post(
        f"/certificados/{cert.certificado_id}/assinar",
        json={"data": base64.b64encode(b"test data").decode(), "url": "https://notallowed.com/path"}
    )

    assert resp.status_code == 403
    assert "dominio nao autorizado" in resp.json()["detail"]


def test_assinar_url_http_bloqueia(signing_client, db_session, user_id, empresa_id):
    """Signing with HTTP URL (not HTTPS) should fail."""
    plano, grupo, cert, grupo_cert = _setup_completo(db_session, user_id, empresa_id)

    criar_regra_acesso(
        db_session,
        empresa_id=empresa_id,
        grupo_id=grupo.grupo_id,
        tipo_dia="corridos",
        horarios=_janela_inclui_agora(),
    )

    _setup_url_permitida(db_session, empresa_id, grupo_cert.grupo_cert_id, "https://example.com")

    resp = signing_client.post(
        f"/certificados/{cert.certificado_id}/assinar",
        json={"data": base64.b64encode(b"test data").decode(), "url": "http://example.com"}
    )

    assert resp.status_code == 403
    assert "apenas URLs HTTPS" in resp.json()["detail"]


def test_assinar_url_dominio_match_ignora_path(signing_client, db_session, user_id, empresa_id):
    """Domain matching should ignore path."""
    plano, grupo, cert, grupo_cert = _setup_completo(db_session, user_id, empresa_id)

    criar_regra_acesso(
        db_session,
        empresa_id=empresa_id,
        grupo_id=grupo.grupo_id,
        tipo_dia="corridos",
        horarios=_janela_inclui_agora(),
    )

    # Allowed URL has no path
    _setup_url_permitida(db_session, empresa_id, grupo_cert.grupo_cert_id, "https://example.com")

    # Request URL has path - should still match
    resp = signing_client.post(
        f"/certificados/{cert.certificado_id}/assinar",
        json={"data": base64.b64encode(b"test data").decode(), "url": "https://example.com/some/deep/path"}
    )

    assert resp.status_code == 200


def test_assinar_url_sem_urls_permitidas_bloqueia(signing_client, db_session, user_id, empresa_id):
    """Signing with no allowed URLs configured should fail."""
    plano, grupo, cert, grupo_cert = _setup_completo(db_session, user_id, empresa_id)

    criar_regra_acesso(
        db_session,
        empresa_id=empresa_id,
        grupo_id=grupo.grupo_id,
        tipo_dia="corridos",
        horarios=_janela_inclui_agora(),
    )

    # No URLs configured

    resp = signing_client.post(
        f"/certificados/{cert.certificado_id}/assinar",
        json={"data": base64.b64encode(b"test data").decode(), "url": "https://example.com"}
    )

    assert resp.status_code == 403
    assert "dominio nao autorizado" in resp.json()["detail"]


# ============================================
# COMBINED TESTS
# ============================================

def test_assinar_todas_validacoes_passam(signing_client, db_session, user_id, empresa_id):
    """Test signing when all validations pass."""
    plano, grupo, cert, grupo_cert = _setup_completo(db_session, user_id, empresa_id)

    hoje = _iso_weekday()

    criar_regra_acesso(
        db_session,
        empresa_id=empresa_id,
        grupo_id=grupo.grupo_id,
        tipo_dia="especificos",
        dias_especificos=[hoje],
        horarios=_janela_inclui_agora(),
        bloquear_em_feriado=True,  # No holiday today
    )

    _setup_url_permitida(db_session, empresa_id, grupo_cert.grupo_cert_id, "https://allowed.com")

    resp = signing_client.post(
        f"/certificados/{cert.certificado_id}/assinar",
        json={"data": base64.b64encode(b"test data").decode(), "url": "https://allowed.com/path"}
    )

    assert resp.status_code == 200
    assert "signature" in resp.json()


def test_assinar_regra_permite_mas_feriado_bloqueia(signing_client, db_session, user_id, empresa_id):
    """Test that holiday blocks even when rule allows."""
    plano, grupo, cert, grupo_cert = _setup_completo(db_session, user_id, empresa_id)

    criar_regra_acesso(
        db_session,
        empresa_id=empresa_id,
        grupo_id=grupo.grupo_id,
        tipo_dia="corridos",
        horarios=_janela_inclui_agora(),
        bloquear_em_feriado=True,
    )

    # Create holiday
    hoje = datetime.now().date()
    criar_feriado(db_session, empresa_id, hoje, nome="Feriado Bloqueador")

    _setup_url_permitida(db_session, empresa_id, grupo_cert.grupo_cert_id, "https://example.com")

    resp = signing_client.post(
        f"/certificados/{cert.certificado_id}/assinar",
        json={"data": base64.b64encode(b"test data").decode(), "url": "https://example.com"}
    )

    assert resp.status_code == 403


def test_assinar_regra_permite_mas_url_bloqueia(signing_client, db_session, user_id, empresa_id):
    """Test that URL validation blocks even when rule allows."""
    plano, grupo, cert, grupo_cert = _setup_completo(db_session, user_id, empresa_id)

    criar_regra_acesso(
        db_session,
        empresa_id=empresa_id,
        grupo_id=grupo.grupo_id,
        tipo_dia="corridos",
        horarios=_janela_inclui_agora(),
    )

    # Setup allowed URL for different domain
    _setup_url_permitida(db_session, empresa_id, grupo_cert.grupo_cert_id, "https://allowed.com")

    resp = signing_client.post(
        f"/certificados/{cert.certificado_id}/assinar",
        json={"data": base64.b64encode(b"test data").decode(), "url": "https://notallowed.com"}
    )

    assert resp.status_code == 403
    assert "dominio nao autorizado" in resp.json()["detail"]


# ============================================
# CERTIFICATE NOT FOUND / NO ACCESS TESTS
# ============================================

def test_assinar_certificado_nao_encontrado(signing_client, db_session, user_id, empresa_id):
    """Signing with non-existent certificate should fail with 404."""
    fake_cert_id = str(uuid.uuid4())

    resp = signing_client.post(
        f"/certificados/{fake_cert_id}/assinar",
        json={"data": base64.b64encode(b"test data").decode(), "url": "https://example.com"}
    )

    assert resp.status_code == 404
    assert "nao encontrado" in resp.json()["detail"]


def test_assinar_usuario_sem_grupo_acesso(signing_client, db_session, user_id, empresa_id):
    """User not in grupo should not access certificate."""
    # Create certificate but don't add user to grupo
    plano = criar_plano(db_session, empresa_id)
    grupo = criar_grupo(db_session, empresa_id, plano.plano_id)
    cert = criar_certificado(db_session, empresa_id, user_id)
    cert.cofre_cert_id = str(uuid.uuid4())
    db_session.commit()

    vincular_certificado_ao_grupo(db_session, empresa_id, grupo.grupo_id, cert.certificado_id)
    # Note: user is NOT added to grupo

    resp = signing_client.post(
        f"/certificados/{cert.certificado_id}/assinar",
        json={"data": base64.b64encode(b"test data").decode(), "url": "https://example.com"}
    )

    assert resp.status_code == 403
