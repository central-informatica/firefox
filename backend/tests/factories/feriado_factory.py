from backend.app.db.models import Feriado
from tests.factories.base import commit_and_refresh

def criar_feriado(
    db,
    empresa_id: int,
    data,  # datetime.date
    nome: str = "Feriado de teste",
    recorrente: bool = False,
):
    feriado = Feriado(
        empresa_id=empresa_id,
        data=data,
        nome=nome,
        recorrente=recorrente,
    )
    return commit_and_refresh(db, feriado)
