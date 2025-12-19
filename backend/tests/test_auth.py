from tests.factories.usuario_factory import criar_usuario

# ----------------------------
# Login com sucesso
# ----------------------------
def test_login_sucesso(client, db_session):
    criar_usuario(db_session)

    response = client.post(
        "/login",
        data={"nome": "Admin", "senha": "123456"}
    )

    assert response.status_code == 200
    body = response.json()
    assert "token" in body
    assert body["status"] == "ok"


# ----------------------------
# Usuário inexistente
# ----------------------------
def test_login_usuario_inexistente(client):
    response = client.post(
        "/login",
        data={"nome": "ghost", "senha": "123456"}
    )

    assert response.status_code == 401


# ----------------------------
# Senha inválida
# ----------------------------
def test_login_senha_invalida(client, db_session):
    criar_usuario(db_session, senha="123456")

    response = client.post(
        "/login",
        data={"nome": "Admin", "senha": "errada"}
    )

    assert response.status_code == 401
