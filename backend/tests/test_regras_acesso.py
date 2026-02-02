from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

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


ENDPOINT_DISPONIVEIS = "/certificados/disponiveis"  # ajuste se necessário


def _now_empresa(timezone: str) -> datetime:
    return datetime.now(tz=ZoneInfo(timezone))


def _janela_inclui_agora(timezone: str):
    now = _now_empresa(timezone)
    ini = (now - timedelta(minutes=5)).strftime("%H:%M")
    fim = (now + timedelta(minutes=5)).strftime("%H:%M")
    return [{"inicio": ini, "fim": fim}]


def _janela_exclui_agora(timezone: str):
    now = _now_empresa(timezone)
    ini = (now - timedelta(minutes=30)).strftime("%H:%M")
    fim = (now - timedelta(minutes=20)).strftime("%H:%M")  # termina antes do "now"
    return [{"inicio": ini, "fim": fim}]


def _iso_dow(timezone: str) -> int:
    # 1 = segunda ... 7 = domingo
    return int(_now_empresa(timezone).isoweekday())


def _setup_basico(db_session, *, timezone="America/Sao_Paulo"):
    admin = criar_usuario(db_session)
    empresa = criar_empresa(db_session, admin.usuario_id)
    # garantir timezone consistente
    empresa.timezone = timezone
    db_session.commit()
    db_session.refresh(empresa)

    adicionar_membro_empresa(db_session, empresa.empresa_id, admin.usuario_id)

    plano = criar_plano(db_session, empresa.empresa_id)
    grupo = criar_grupo(db_session, empresa.empresa_id, plano.plano_id)

    # usuário que vai consultar
    usuario = criar_usuario(db_session, nome="User", email="user@test.com")
    adicionar_membro_empresa(db_session, empresa.empresa_id, usuario.usuario_id)
    adicionar_usuario_ao_grupo(db_session, empresa.empresa_id, grupo.grupo_id, usuario.usuario_id)

    # certificado + vínculo com o grupo
    cert = criar_certificado(db_session, empresa.empresa_id, admin.usuario_id)
    vincular_certificado_ao_grupo(db_session, empresa.empresa_id, grupo.grupo_id, cert.certificado_id)

    return admin, usuario, empresa, grupo, cert


def test_corridos_permite_quando_dentro_do_horario(client, db_session):
    admin, usuario, empresa, grupo, cert = _setup_basico(db_session)

    # Regra corridos incluindo agora
    criar_regra_acesso(
        db_session,
        empresa_id=empresa.empresa_id,
        grupo_id=grupo.grupo_id,
        tipo_dia="corridos",
        horarios=_janela_inclui_agora(empresa.timezone),
    )

    client = autenticar(client, db_session, lambda db: usuario)

    resp = client.get(ENDPOINT_DISPONIVEIS)
    assert resp.status_code == 200

    itens = resp.json()
    assert len(itens) == 1
    assert itens[0]["certificado_id"] == cert.certificado_id
    assert itens[0]["pode_acessar"] is True


def test_corridos_bloqueia_quando_fora_do_horario(client, db_session):
    admin, usuario, empresa, grupo, cert = _setup_basico(db_session)

    # Regra corridos excluindo agora
    criar_regra_acesso(
        db_session,
        empresa_id=empresa.empresa_id,
        grupo_id=grupo.grupo_id,
        tipo_dia="corridos",
        horarios=_janela_exclui_agora(empresa.timezone),
    )

    client = autenticar(client, db_session, lambda db: usuario)

    resp = client.get(ENDPOINT_DISPONIVEIS)
    assert resp.status_code == 200

    itens = resp.json()
    assert len(itens) == 1
    assert itens[0]["pode_acessar"] is False


def test_especificos_respeita_dia_da_semana(client, db_session):
    admin, usuario, empresa, grupo, cert = _setup_basico(db_session)

    hoje = _iso_dow(empresa.timezone)

    # Regra que permite HOJE
    criar_regra_acesso(
        db_session,
        empresa_id=empresa.empresa_id,
        grupo_id=grupo.grupo_id,
        tipo_dia="especificos",
        dias_especificos=[hoje],
        horarios=_janela_inclui_agora(empresa.timezone),
    )

    client = autenticar(client, db_session, lambda db: usuario)

    resp = client.get(ENDPOINT_DISPONIVEIS)
    assert resp.status_code == 200
    assert resp.json()[0]["pode_acessar"] is True

    # Agora trocamos a regra para NÃO permitir hoje (limpa e cria outra)
    db_session.query(type(db_session.query.__self__)).all()  # no-op (evita lint); pode remover

def test_especificos_respeita_dia_da_semana(client, db_session):
    admin, usuario, empresa, grupo, cert = _setup_basico(db_session)

    hoje = _iso_dow(empresa.timezone)
    outro_dia = 1 if hoje != 1 else 2

    # 1) Regra que permite HOJE
    criar_regra_acesso(
        db_session,
        empresa_id=empresa.empresa_id,
        grupo_id=grupo.grupo_id,
        tipo_dia="especificos",
        dias_especificos=[hoje],
        horarios=_janela_inclui_agora(empresa.timezone),
    )

    client = autenticar(client, db_session, lambda db: usuario)

    resp = client.get(ENDPOINT_DISPONIVEIS)
    assert resp.status_code == 200
    assert resp.json()[0]["pode_acessar"] is True

    # 2) Remove a regra anterior criando um novo grupo/cert para cenário "nega"
    # (garante isolamento sem depender de delete de regra/endpoint)
    grupo2 = criar_grupo(db_session, empresa.empresa_id, criar_plano(db_session, empresa.empresa_id).plano_id, nome="Grupo 2")
    adicionar_usuario_ao_grupo(db_session, empresa.empresa_id, grupo2.grupo_id, usuario.usuario_id)

    cert2 = criar_certificado(db_session, empresa.empresa_id, admin.usuario_id, nome_arquivo="outro.pfx")
    vincular_certificado_ao_grupo(db_session, empresa.empresa_id, grupo2.grupo_id, cert2.certificado_id)

    criar_regra_acesso(
        db_session,
        empresa_id=empresa.empresa_id,
        grupo_id=grupo2.grupo_id,
        tipo_dia="especificos",
        dias_especificos=[outro_dia],  # NÃO inclui hoje
        horarios=_janela_inclui_agora(empresa.timezone),
    )

    resp2 = client.get(ENDPOINT_DISPONIVEIS)
    assert resp2.status_code == 200

    by_id = {c["certificado_id"]: c for c in resp2.json()}
    assert by_id[cert2.certificado_id]["pode_acessar"] is False


def test_feriado_bloqueia_mesmo_com_regra_permitindo(client, db_session):
    admin, usuario, empresa, grupo, cert = _setup_basico(db_session)

    # Regra permite agora
    criar_regra_acesso(
        db_session,
        empresa_id=empresa.empresa_id,
        grupo_id=grupo.grupo_id,
        tipo_dia="corridos",
        horarios=_janela_inclui_agora(empresa.timezone),
    )

    # Cria feriado para HOJE no timezone da empresa
    hoje_date = _now_empresa(empresa.timezone).date()
    criar_feriado(db_session, empresa.empresa_id, hoje_date, nome="Feriado Hoje", recorrente=False)

    client = autenticar(client, db_session, lambda db: usuario)

    resp = client.get(ENDPOINT_DISPONIVEIS)
    assert resp.status_code == 200
    assert resp.json()[0]["pode_acessar"] is False

