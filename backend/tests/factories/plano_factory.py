from backend.app.db.models import PlanosTrabalho
from tests.factories.base import commit_and_refresh

from tests.factories.usuario_factory import criar_usuario
from tests.factories.empresa_factory import criar_empresa
from tests.factories.empresa_membro_factory import adicionar_membro_empresa
from tests.factories.plano_factory import criar_plano
from tests.utils.auth import autenticar


def criar_plano(
    db,
    empresa_id,
    nome="Plano Padrão",
    descricao="Plano de trabalho padrão",
):
    plano = PlanosTrabalho(
        empresa_id=empresa_id,
        nome=nome,
        descricao=descricao,
    )
    return commit_and_refresh(db, plano)


def test_criar_plano_trabalho(client, db_session):
    usuario = criar_usuario(db_session)
    client = autenticar(client, db_session, criar_usuario)

    empresa = criar_empresa(db_session, usuario.usuario_id)
    adicionar_membro_empresa(db_session, empresa.empresa_id, usuario.usuario_id)

    payload = {
        "empresa_id": empresa.empresa_id,
        "nome": "Plano Financeiro",
        "descricao": "Plano para setor financeiro",
    }

    response = client.post("/planos-trabalho", json=payload)

    assert response.status_code == 201
    assert response.json()["nome"] == "Plano Financeiro"

def test_plano_nome_duplicado_na_mesma_empresa(client, db_session):
    usuario = criar_usuario(db_session)
    client = autenticar(client, db_session, criar_usuario)

    empresa = criar_empresa(db_session, usuario.usuario_id)
    adicionar_membro_empresa(db_session, empresa.empresa_id, usuario.usuario_id)

    criar_plano(db_session, empresa.empresa_id, nome="Duplicado")

    payload = {
        "empresa_id": empresa.empresa_id,
        "nome": "Duplicado",
    }

    response = client.post("/planos-trabalho", json=payload)

    assert response.status_code == 400

def test_listar_planos_trabalho(client, db_session):
    usuario = criar_usuario(db_session)
    client = autenticar(client, db_session, criar_usuario)

    empresa = criar_empresa(db_session, usuario.usuario_id)
    adicionar_membro_empresa(db_session, empresa.empresa_id, usuario.usuario_id)

    criar_plano(db_session, empresa.empresa_id, nome="Plano A")
    criar_plano(db_session, empresa.empresa_id, nome="Plano B")

    response = client.get(f"/planos-trabalho?empresa_id={empresa.empresa_id}")

    assert response.status_code == 200
    assert len(response.json()) == 2

def test_buscar_plano_por_id(client, db_session):
    usuario = criar_usuario(db_session)
    client = autenticar(client, db_session, criar_usuario)

    empresa = criar_empresa(db_session, usuario.usuario_id)
    adicionar_membro_empresa(db_session, empresa.empresa_id, usuario.usuario_id)

    plano = criar_plano(db_session, empresa.empresa_id)

    response = client.get(f"/planos-trabalho/{plano.plano_id}")

    assert response.status_code == 200
    assert response.json()["plano_id"] == plano.plano_id

def test_editar_plano_trabalho(client, db_session):
    usuario = criar_usuario(db_session)
    client = autenticar(client, db_session, criar_usuario)

    empresa = criar_empresa(db_session, usuario.usuario_id)
    adicionar_membro_empresa(db_session, empresa.empresa_id, usuario.usuario_id)

    plano = criar_plano(db_session, empresa.empresa_id)

    payload = {
        "nome": "Plano Atualizado",
        "descricao": "Descrição atualizada",
    }

    response = client.put(f"/planos-trabalho/{plano.plano_id}", json=payload)

    assert response.status_code == 200
    assert response.json()["nome"] == "Plano Atualizado"

def test_plano_nao_acessivel_por_outro_usuario(client, db_session):
    # Usuário A
    usuario_a = criar_usuario(db_session, email="a@a.com")
    empresa_a = criar_empresa(db_session, usuario_a.usuario_id)
    adicionar_membro_empresa(db_session, empresa_a.empresa_id, usuario_a.usuario_id)
    plano = criar_plano(db_session, empresa_a.empresa_id)

    # Usuário B
    usuario_b = criar_usuario(db_session, nome="B", email="b@b.com")
    client = autenticar(client, db_session, lambda db: usuario_b)

    response = client.get(f"/planos-trabalho/{plano.plano_id}")

    assert response.status_code in (403, 404)

def test_listar_planos_sem_login(client):
    response = client.get("/planos-trabalho")
    assert response.status_code == 401
