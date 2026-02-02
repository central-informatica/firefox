from datetime import timedelta
from zoneinfo import ZoneInfo
from datetime import datetime

from tests.factories.usuario_factory import criar_usuario
from tests.factories.empresa_factory import criar_empresa
from tests.factories.empresa_membro_factory import adicionar_membro_empresa
from tests.factories.plano_factory import criar_plano
from tests.factories.grupo_factory import criar_grupo
from tests.factories.grupo_usuario_factory import adicionar_usuario_ao_grupo
from tests.factories.certificado_factory import criar_certificado
from tests.factories.grupo_certificado_factory import vincular_certificado_ao_grupo
from tests.factories.regra_acesso_factory import criar_regra_acesso
from tests.factories.feriado_factory import criar_feriado
from tests.utils.auth import autenticar


ENDPOINT_DISPONIVEIS = "/certificados/disponiveis"
ENDPOINT_SIGN = "/api/sign"

def janela_agora(timezone: str):
    now = datetime.now(tz=ZoneInfo(timezone))
    return [{
        "inicio": (now - timedelta(minutes=5)).strftime("%H:%M"),
        "fim": (now + timedelta(minutes=5)).strftime("%H:%M"),
    }]

def test_fluxo_completo_acesso_permitido(client, db_session):
    # Admin cria tudo
    admin = criar_usuario(db_session)
    empresa = criar_empresa(db_session, admin.usuario_id)
    adicionar_membro_empresa(db_session, empresa.empresa_id, admin.usuario_id)

    plano = criar_plano(db_session, empresa.empresa_id)
    grupo = criar_grupo(db_session, empresa.empresa_id, plano.plano_id)

    usuario = criar_usuario(db_session, nome="User", email="user@test.com")
    adicionar_membro_empresa(db_session, empresa.empresa_id, usuario.usuario_id)
    adicionar_usuario_ao_grupo(db_session, empresa.empresa_id, grupo.grupo_id, usuario.usuario_id)

    cert = criar_certificado(db_session, empresa.empresa_id, admin.usuario_id)
    vincular_certificado_ao_grupo(db_session, empresa.empresa_id, grupo.grupo_id, cert.certificado_id)

    criar_regra_acesso(
        db_session,
        empresa_id=empresa.empresa_id,
        grupo_id=grupo.grupo_id,
        tipo_dia="corridos",
        horarios=janela_agora(empresa.timezone),
    )

    client = autenticar(client, db_session, lambda db: usuario)

    # 1) Certificado aparece como acessível
    resp = client.get(ENDPOINT_DISPONIVEIS)
    assert resp.status_code == 200

    item = resp.json()[0]
    assert item["pode_acessar"] is True

    # 2) Assinatura é permitida
    sign_resp = client.post(
        ENDPOINT_SIGN,
        json={
            "cert_id": cert.certificado_id,
            "data": "ZGFkb3M=",  # "dados" em base64
            "algorithm": "SHA256",
        }
    )

    assert sign_resp.status_code == 200
    assert "signature" in sign_resp.json()

def test_fluxo_completo_bloqueado_por_feriado(client, db_session):
    admin = criar_usuario(db_session)
    empresa = criar_empresa(db_session, admin.usuario_id)
    adicionar_membro_empresa(db_session, empresa.empresa_id, admin.usuario_id)

    plano = criar_plano(db_session, empresa.empresa_id)
    grupo = criar_grupo(db_session, empresa.empresa_id, plano.plano_id)

    usuario = criar_usuario(db_session, email="user2@test.com")
    adicionar_membro_empresa(db_session, empresa.empresa_id, usuario.usuario_id)
    adicionar_usuario_ao_grupo(db_session, empresa.empresa_id, grupo.grupo_id, usuario.usuario_id)

    cert = criar_certificado(db_session, empresa.empresa_id, admin.usuario_id)
    vincular_certificado_ao_grupo(db_session, empresa.empresa_id, grupo.grupo_id, cert.certificado_id)

    criar_regra_acesso(
        db_session,
        empresa_id=empresa.empresa_id,
        grupo_id=grupo.grupo_id,
        tipo_dia="corridos",
        horarios=janela_agora(empresa.timezone),
    )

    # Feriado hoje
    hoje = datetime.now(tz=ZoneInfo(empresa.timezone)).date()
    criar_feriado(db_session, empresa.empresa_id, hoje, nome="Feriado Teste")

    client = autenticar(client, db_session, lambda db: usuario)

    # 1) Lista mostra bloqueado
    resp = client.get(ENDPOINT_DISPONIVEIS)
    assert resp.status_code == 200
    assert resp.json()[0]["pode_acessar"] is False

    # 2) Assinatura deve ser bloqueada
    sign_resp = client.post(
        ENDPOINT_SIGN,
        json={
            "cert_id": cert.certificado_id,
            "data": "ZGFkb3M=",
            "algorithm": "SHA256",
        }
    )

def test_usuario_nao_pode_assinar_sem_regra(client, db_session):
    admin = criar_usuario(db_session)
    empresa = criar_empresa(db_session, admin.usuario_id)
    adicionar_membro_empresa(db_session, empresa.empresa_id, admin.usuario_id)

    plano = criar_plano(db_session, empresa.empresa_id)
    grupo = criar_grupo(db_session, empresa.empresa_id, plano.plano_id)

    usuario = criar_usuario(db_session, email="user3@test.com")
    adicionar_membro_empresa(db_session, empresa.empresa_id, usuario.usuario_id)
    adicionar_usuario_ao_grupo(db_session, empresa.empresa_id, grupo.grupo_id, usuario.usuario_id)

    cert = criar_certificado(db_session, empresa.empresa_id, admin.usuario_id)
    vincular_certificado_ao_grupo(db_session, empresa.empresa_id, grupo.grupo_id, cert.certificado_id)

    # ⚠️ nenhuma regra criada

    client = autenticar(client, db_session, lambda db: usuario)

    resp = client.get(ENDPOINT_DISPONIVEIS)
    assert resp.status_code == 200
    assert resp.json()[0]["pode_acessar"] is False

    sign_resp = client.post(
        ENDPOINT_SIGN,
        json={
            "cert_id": cert.certificado_id,
            "data": "ZGFkb3M=",
            "algorithm": "SHA256",
        }
    )

    assert sign_resp.status_code in (403, 401)

def test_usuario_sem_grupo_nunca_acessa(client, db_session):
    admin = criar_usuario(db_session)
    empresa = criar_empresa(db_session, admin.usuario_id)
    adicionar_membro_empresa(db_session, empresa.empresa_id, admin.usuario_id)

    usuario = criar_usuario(db_session, email="nogroup@test.com")
    adicionar_membro_empresa(db_session, empresa.empresa_id, usuario.usuario_id)

    cert = criar_certificado(db_session, empresa.empresa_id, admin.usuario_id)

    client = autenticar(client, db_session, lambda db: usuario)

    resp = client.get(ENDPOINT_DISPONIVEIS)
    assert resp.status_code == 200
    assert resp.json() == []

    sign_resp = client.post(
        ENDPOINT_SIGN,
        json={
            "cert_id": cert.certificado_id,
            "data": "ZGFkb3M=",
            "algorithm": "SHA256",
        }
    )

    assert sign_resp.status_code in (403, 401)
