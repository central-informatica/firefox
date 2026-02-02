def autenticar(client, db, criar_usuario_fn):
    criar_usuario_fn(db)

    response = client.post(
        "/login",
        data={"nome": "Admin", "senha": "123456"}
    )

    assert response.status_code == 200
    return client
