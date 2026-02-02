from tests.factories.usuario_factory import criar_usuario
from tests.factories.empresa_factory import criar_empresa
from tests.factories.empresa_membro_factory import adicionar_membro_empresa
from tests.factories.plano_factory import criar_plano
from tests.factories.grupo_factory import criar_grupo
from tests.factories.grupo_usuario_factory import adicionar_usuario_ao_grupo
from tests.utils.auth import autenticar

def test_adicionar_usuario_ao_grupo(client, db_session):
    # Admin
    admin = criar_usuario(db_session)
    client = autenticar(client, db_session, criar_usuario)

    empresa = criar_empresa(db_session, admin.usuario_id)
    adicionar_membro_empresa(db_session, empresa.empresa_id, admin.usuario_id)

    plano = criar_plano(db_session, empresa.empresa_id)
    grupo = criar_grupo(db_session, empresa.empresa_id, plano.plano_id)

    # Usuário comum
    usuario = criar_usuario(
        db_session,
        nome="User",
        email="user@test.com"
    )
    adicionar_membro_empresa(db_session, empresa.empresa_id, usuario.usuario_id)

    response = client.post(
        f"/grupos/{grupo.grupo_id}/usuarios",
        json={"usuario_id": usuario.usuario_id}
    )

    assert response.status_code == 201

def test_usuario_duplicado_no_grupo(client, db_session):
    admin = criar_usuario(db_session)
    client = autenticar(client, db_session, criar_usuario)

    empresa = criar_empresa(db_session, admin.usuario_id)
    adicionar_membro_empresa(db_session, empresa.empresa_id, admin.usuario_id)

    plano = criar_plano(db_session, empresa.empresa_id)
    grupo = criar_grupo(db_session, empresa.empresa_id, plano.plano_id)

    usuario = criar_usuario(db_session, email="dup@test.com")
    adicionar_membro_empresa(db_session, empresa.empresa_id, usuario.usuario_id)
    adicionar_usuario_ao_grupo(
        db_session, empresa.empresa_id, grupo.grupo_id, usuario.usuario_id
    )

    response = client.post(
        f"/grupos/{grupo.grupo_id}/usuarios",
        json={"usuario_id": usuario.usuario_id}
    )

    assert response.status_code == 400

def test_listar_usuarios_do_grupo(client, db_session):
    admin = criar_usuario(db_session)
    client = autenticar(client, db_session, criar_usuario)

    empresa = criar_empresa(db_session, admin.usuario_id)
    adicionar_membro_empresa(db_session, empresa.empresa_id, admin.usuario_id)

    plano = criar_plano(db_session, empresa.empresa_id)
    grupo = criar_grupo(db_session, empresa.empresa_id, plano.plano_id)

    usuario = criar_usuario(db_session, email="list@test.com")
    adicionar_membro_empresa(db_session, empresa.empresa_id, usuario.usuario_id)
    adicionar_usuario_ao_grupo(
        db_session, empresa.empresa_id, grupo.grupo_id, usuario.usuario_id
    )

    response = client.get(f"/grupos/{grupo.grupo_id}/usuarios")

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_remover_usuario_do_grupo(client, db_session):
    admin = criar_usuario(db_session)
    client = autenticar(client, db_session, criar_usuario)

    empresa = criar_empresa(db_session, admin.usuario_id)
    adicionar_membro_empresa(db_session, empresa.empresa_id, admin.usuario_id)

    plano = criar_plano(db_session, empresa.empresa_id)
    grupo = criar_grupo(db_session, empresa.empresa_id, plano.plano_id)

    usuario = criar_usuario(db_session, email="rem@test.com")
    adicionar_membro_empresa(db_session, empresa.empresa_id, usuario.usuario_id)
    adicionar_usuario_ao_grupo(
        db_session, empresa.empresa_id, grupo.grupo_id, usuario.usuario_id
    )

    response = client.delete(
        f"/grupos/{grupo.grupo_id}/usuarios/{usuario.usuario_id}"
    )

    assert response.status_code == 204

def test_nao_adiciona_usuario_de_outra_empresa(client, db_session):
    # Empresa A
    admin_a = criar_usuario(db_session, email="a@test.com")
    empresa_a = criar_empresa(db_session, admin_a.usuario_id)
    adicionar_membro_empresa(db_session, empresa_a.empresa_id, admin_a.usuario_id)

    plano = criar_plano(db_session, empresa_a.empresa_id)
    grupo = criar_grupo(db_session, empresa_a.empresa_id, plano.plano_id)

    # Empresa B
    admin_b = criar_usuario(db_session, email="b@test.com")
    empresa_b = criar_empresa(db_session, admin_b.usuario_id)
    adicionar_membro_empresa(db_session, empresa_b.empresa_id, admin_b.usuario_id)

    client = autenticar(client, db_session, lambda db: admin_b)

    response = client.post(
        f"/grupos/{grupo.grupo_id}/usuarios",
        json={"usuario_id": admin_b.usuario_id}
    )

    assert response.status_code in (403, 404)

def test_adicionar_usuario_sem_login(client):
    response = client.post("/grupos/1/usuarios", json={"usuario_id": 1})
    assert response.status_code == 401

