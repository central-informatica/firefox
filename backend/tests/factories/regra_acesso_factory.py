from backend.app.db.models import RegrasAcesso
from tests.factories.base import commit_and_refresh

def criar_regra_acesso(
    db,
    empresa_id: int,
    grupo_id: int,
    tipo_dia: str = "corridos",  # corridos | uteis | especificos
    dias_especificos=None,       # list[int] (1..7)
    horarios=None,               # list[{"inicio":"HH:MM","fim":"HH:MM"}]
):
    if horarios is None:
        horarios = [{"inicio": "00:00", "fim": "23:59"}]

    regra = RegrasAcesso(
        empresa_id=empresa_id,
        grupo_id=grupo_id,
        tipo_dia=tipo_dia,
        dias_especificos=dias_especificos,
        horarios=horarios,
    )
    return commit_and_refresh(db, regra)
