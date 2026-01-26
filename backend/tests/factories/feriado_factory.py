from backend.app.db.models import Feriados
from tests.factories.base import commit_and_refresh

def criar_feriado(
    db,
    empresa_id,
    data,  # datetime.date
    nome: str = "Feriado de teste",
    recorrente: bool = False,
):
    feriado = Feriados(
        empresa_id=empresa_id,
        data=data,
        nome=nome,
        recorrente=recorrente,
    )
    return commit_and_refresh(db, feriado)
