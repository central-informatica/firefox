from tests.factories.usuario_factory import criar_usuario
from tests.factories.empresa_factory import criar_empresa
from tests.factories.empresa_membro_factory import adicionar_membro_empresa
from tests.factories.plano_factory import criar_plano
from tests.factories.grupo_factory import criar_grupo
from tests.factories.grupo_usuario_factory import adicionar_usuario_ao_grupo
from tests.utils.auth import autenticar

def test_criar_grupo(client, db_session):
    usuario = criar_usuario(db_session)
    client = autenticar(client, db_session, criar_usuario)

    empresa = criar_empresa(db_session, usuario.usuario_id)
    adicionar_membro_empresa(db_session, empresa.empresa_id, usuario.usuario_id)

    plano = criar_plano(db_session, empresa.empresa_id)

    payload = {
        "empresa_id": empresa.empresa_id,
        "plano_id": plano.plano_id,
        "nome": "Grupo Financeiro",
    }

    response = client.post("/grupos", json=payload)

    assert response.status_code == 201
    assert response.json()["nome"] == "Grupo Financeiro"

def test_grupo_nome_duplicado_na_empresa(client, db_session):
    usuario = criar_usuario(db_session)
    client = autenticar(client, db_session, criar_usuario)

    empresa = criar_empresa(db_session, usuario.usuario_id)
    adicionar_membro_empresa(db_session, empresa.empresa_id, usuario.usuario_id)

    plano = criar_plano(db_session, empresa.empresa_id)
    criar_grupo(db_session, empresa.empresa_id, plano.plano_id, nome="Duplicado")

    payload = {
        "empresa_id": empresa.empresa_id,
        "plano_id": plano.plano_id,
        "nome": "Duplicado",
    }

    response = client.post("/grupos", json=payload)

    assert response.status_code == 400

def test_listar_grupos_por_plano(client, db_session):
    usuario = criar_usuario(db_session)
    client = autenticar(client, db_session, criar_usuario)

    empresa = criar_empresa(db_session, usuario.usuario_id)
    adicionar_membro_empresa(db_session, empresa.empresa_id, usuario.usuario_id)

    plano = criar_plano(db_session, empresa.empresa_id)

    criar_grupo(db_session, empresa.empresa_id, plano.plano_id, nome="Grupo A")
    criar_grupo(db_session, empresa.empresa_id, plano.plano_id, nome="Grupo B")

    response = client.get(f"/grupos?plano_id={plano.plano_id}")

    assert response.status_code == 200
    assert len(response.json()) == 2

def test_buscar_grupo_por_id(client, db_session):
    usuario = criar_usuario(db_session)
    client = autenticar(client, db_session, criar_usuario)

    empresa = criar_empresa(db_session, usuario.usuario_id)
    adicionar_membro_empresa(db_session, empresa.empresa_id, usuario.usuario_id)

    plano = criar_plano(db_session, empresa.empresa_id)
    grupo = criar_grupo(db_session, empresa.empresa_id, plano.plano_id)

    response = client.get(f"/grupos/{grupo.grupo_id}")

    assert response.status_code == 200
    assert response.json()["grupo_id"] == grupo.grupo_id

def test_editar_grupo(client, db_session):
    usuario = criar_usuario(db_session)
    client = autenticar(client, db_session, criar_usuario)

    empresa = criar_empresa(db_session, usuario.usuario_id)
    adicionar_membro_empresa(db_session, empresa.empresa_id, usuario.usuario_id)

    plano = criar_plano(db_session, empresa.empresa_id)
    grupo = criar_grupo(db_session, empresa.empresa_id, plano.plano_id)

    payload = {"nome": "Grupo Atualizado"}

    response = client.put(f"/grupos/{grupo.grupo_id}", json=payload)

    assert response.status_code == 200
    assert response.json()["nome"] == "Grupo Atualizado"


def test_grupo_nao_acessivel_por_outro_usuario(client, db_session):
    # Usuário A
    usuario_a = criar_usuario(db_session, email="a@a.com")
    empresa_a = criar_empresa(db_session, usuario_a.usuario_id)
    adicionar_membro_empresa(db_session, empresa_a.empresa_id, usuario_a.usuario_id)
    plano = criar_plano(db_session, empresa_a.empresa_id)
    grupo = criar_grupo(db_session, empresa_a.empresa_id, plano.plano_id)

    # Usuário B
    usuario_b = criar_usuario(db_session, nome="B", email="b@b.com")
    client = autenticar(client, db_session, lambda db: usuario_b)

    response = client.get(f"/grupos/{grupo.grupo_id}")

    assert response.status_code in (403, 404)

def test_listar_grupos_sem_login(client):
    response = client.get("/grupos")
    assert response.status_code == 401

