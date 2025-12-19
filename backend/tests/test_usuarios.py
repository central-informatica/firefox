from tests.factories.usuario_factory import criar_usuario
from tests.utils.auth import autenticar

def test_criar_usuario(client):
    payload = {
        "nome": "João Silva",
        "email": "joao@test.com",
        "senha": "123456"
    }

    response = client.post("/usuarios", json=payload)

    assert response.status_code == 201
    body = response.json()

    assert body["nome"] == "João Silva"
    assert body["email"] == "joao@test.com"

def test_criar_usuario_email_duplicado(client, db_session):
    criar_usuario(db_session, email="dup@test.com")

    payload = {
        "nome": "Outro",
        "email": "dup@test.com",
        "senha": "123456"
    }

    response = client.post("/usuarios", json=payload)

    assert response.status_code == 400

def test_listar_usuarios(client, db_session):
    client = autenticar(client, db_session, criar_usuario)

    response = client.get("/usuarios")

    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_buscar_usuario_por_id(client, db_session):
    client = autenticar(client, db_session, criar_usuario)

    response = client.get("/usuarios/1")

    assert response.status_code == 200
    assert response.json()["usuario_id"] == 1

def test_editar_usuario(client, db_session):
    client = autenticar(client, db_session, criar_usuario)

    payload = {
        "nome": "Admin Alterado",
        "email": "admin@test.com"
    }

    response = client.put("/usuarios/1", json=payload)

    assert response.status_code == 200
    assert response.json()["nome"] == "Admin Alterado"

def test_listar_usuarios_sem_login(client):
    response = client.get("/usuarios")
    assert response.status_code == 401
