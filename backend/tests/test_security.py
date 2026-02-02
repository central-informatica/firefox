def test_rota_protegida_sem_login(client):
    response = client.get("/empresas")
    assert response.status_code == 401
