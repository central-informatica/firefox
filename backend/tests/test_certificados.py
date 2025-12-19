from tests.factories.usuario_factory import criar_usuario
from tests.factories.empresa_factory import criar_empresa
from tests.factories.empresa_membro_factory import adicionar_membro_empresa
from tests.factories.plano_factory import criar_plano
from tests.factories.grupo_factory import criar_grupo
from tests.factories.grupo_usuario_factory import adicionar_usuario_ao_grupo
from tests.factories.certificado_factory import criar_certificado
from tests.utils.auth import autenticar

def test_upload_certificado(client, db_session, tmp_path):
    admin = criar_usuario(db_session)
    client = autenticar(client, db_session, criar_usuario)

    empresa = criar_empresa(db_session, admin.usuario_id)
    adicionar_membro_empresa(db_session, empresa.empresa_id, admin.usuario_id)

    arquivo = tmp_path / "cert.pfx"
    arquivo.write_bytes(b"fake-pfx")

    response = client.post(
        "/certificados/upload",
        files={"arquivo": ("cert.pfx", arquivo.read_bytes())},
        data={"senha": "1234"}
    )

    assert response.status_code == 201

def test_listar_certificados_do_usuario(client, db_session):
    admin = criar_usuario(db_session)
    usuario = criar_usuario(db_session, email="user@test.com")
    client = autenticar(client, db_session, criar_usuario)

    empresa = criar_empresa(db_session, admin.usuario_id)
    adicionar_membro_empresa(db_session, empresa.empresa_id, admin.usuario_id)
    adicionar_membro_empresa(db_session, empresa.empresa_id, usuario.usuario_id)

    plano = criar_plano(db_session, empresa.empresa_id)
    grupo = criar_grupo(db_session, empresa.empresa_id, plano.plano_id)

    adicionar_usuario_ao_grupo(db_session, empresa.empresa_id, grupo.grupo_id, usuario.usuario_id)

    cert = criar_certificado(db_session, empresa.empresa_id, admin.usuario_id)

    response = client.get("/certificados")

    assert response.status_code == 200
    assert len(response.json()) == 1

def test_usuario_sem_grupo_nao_ve_certificado(client, db_session):
    admin = criar_usuario(db_session)
    usuario = criar_usuario(db_session, email="nogroup@test.com")
    client = autenticar(client, db_session, lambda db: usuario)

    empresa = criar_empresa(db_session, admin.usuario_id)
    adicionar_membro_empresa(db_session, empresa.empresa_id, admin.usuario_id)
    adicionar_membro_empresa(db_session, empresa.empresa_id, usuario.usuario_id)

    criar_certificado(db_session, empresa.empresa_id, admin.usuario_id)

    response = client.get("/certificados")

    assert response.status_code == 200
    assert response.json() == []

def test_certificado_nao_visivel_para_outra_empresa(client, db_session):
    # Empresa A
    admin_a = criar_usuario(db_session, email="a@test.com")
    empresa_a = criar_empresa(db_session, admin_a.usuario_id)
    adicionar_membro_empresa(db_session, empresa_a.empresa_id, admin_a.usuario_id)
    criar_certificado(db_session, empresa_a.empresa_id, admin_a.usuario_id)

    # Empresa B
    admin_b = criar_usuario(db_session, email="b@test.com")
    empresa_b = criar_empresa(db_session, admin_b.usuario_id)
    adicionar_membro_empresa(db_session, empresa_b.empresa_id, admin_b.usuario_id)

    client = autenticar(client, db_session, lambda db: admin_b)

    response = client.get("/certificados")

    assert response.status_code == 200
    assert response.json() == []

def test_listar_certificados_sem_login(client):
    response = client.get("/certificados")
    assert response.status_code == 401
