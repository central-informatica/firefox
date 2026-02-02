from tests.factories.usuario_factory import criar_usuario
from tests.factories.empresa_factory import criar_empresa
from tests.factories.empresa_membro_factory import adicionar_membro_empresa
from tests.utils.auth import autenticar

def test_criar_empresa(client, db_session):
    client = autenticar(client, db_session, criar_usuario)

    payload = {
        "razao_social": "Empresa Alpha LTDA",
        "fantasia": "Alpha",
        "cnpj": "11111111000199",
        "timezone": "America/Sao_Paulo",
    }

    response = client.post("/empresas", json=payload)

    assert response.status_code == 201
    body = response.json()

    assert body["razao_social"] == "Empresa Alpha LTDA"
    assert body["cnpj"] == "11111111000199"

def test_listar_empresas_do_usuario(client, db_session):
    usuario = criar_usuario(db_session)
    client = autenticar(client, db_session, criar_usuario)

    empresa = criar_empresa(db_session, usuario.usuario_id)
    adicionar_membro_empresa(db_session, empresa.empresa_id, usuario.usuario_id)

    response = client.get("/empresas")

    assert response.status_code == 200
    assert len(response.json()) == 1

def test_buscar_empresa_por_id(client, db_session):
    usuario = criar_usuario(db_session)
    client = autenticar(client, db_session, criar_usuario)

    empresa = criar_empresa(db_session, usuario.usuario_id)
    adicionar_membro_empresa(db_session, empresa.empresa_id, usuario.usuario_id)

    response = client.get(f"/empresas/{empresa.empresa_id}")

    assert response.status_code == 200
    assert response.json()["empresa_id"] == empresa.empresa_id

def test_editar_empresa(client, db_session):
    usuario = criar_usuario(db_session)
    client = autenticar(client, db_session, criar_usuario)

    empresa = criar_empresa(db_session, usuario.usuario_id)
    adicionar_membro_empresa(db_session, empresa.empresa_id, usuario.usuario_id)

    payload = {
        "razao_social": "Empresa Alterada LTDA",
        "fantasia": "Alterada",
    }

    response = client.put(f"/empresas/{empresa.empresa_id}", json=payload)

    assert response.status_code == 200
    assert response.json()["razao_social"] == "Empresa Alterada LTDA"

def test_usuario_nao_acessa_empresa_de_outro_tenant(client, db_session):
    # Usuário A
    usuario_a = criar_usuario(db_session, email="a@test.com")
    empresa_a = criar_empresa(db_session, usuario_a.usuario_id)
    adicionar_membro_empresa(db_session, empresa_a.empresa_id, usuario_a.usuario_id)

    # Usuário B
    usuario_b = criar_usuario(db_session, nome="B", email="b@test.com")
    client = autenticar(client, db_session, lambda db: usuario_b)

    response = client.get(f"/empresas/{empresa_a.empresa_id}")

    assert response.status_code in (403, 404)

def test_listar_empresas_sem_login(client):
    response = client.get("/empresas")
    assert response.status_code == 401
