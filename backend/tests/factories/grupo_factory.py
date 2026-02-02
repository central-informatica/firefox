from backend.app.db.models import Grupos
from tests.factories.base import commit_and_refresh

def criar_grupo(
    db,
    empresa_id,
    plano_id,
    nome="Grupo Padrão",
):
    grupo = Grupos(
        empresa_id=empresa_id,
        plano_id=plano_id,
        nome=nome,
    )
    return commit_and_refresh(db, grupo)
