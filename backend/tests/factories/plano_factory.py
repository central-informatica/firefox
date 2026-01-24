from backend.app.db.models import PlanosTrabalho
from tests.factories.base import commit_and_refresh


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
