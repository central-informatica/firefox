from backend.app.db.models import Grupos
from tests.factories.base import commit_and_refresh

def criar_grupo(
    db,
    empresa_id=None,
    plano_id=None,
    nome="Grupo Padrão",
):
    # If plano_id not provided, create one
    if not plano_id:
        from tests.factories.plano_factory import criar_plano
        plano = criar_plano(db, empresa_id=empresa_id)
        plano_id = plano.plano_id

    grupo = Grupos(
        empresa_id=empresa_id,
        plano_id=plano_id,
        nome=nome,
    )
    return commit_and_refresh(db, grupo)
