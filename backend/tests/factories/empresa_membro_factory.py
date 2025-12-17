from backend.app.db.models import EmpresaMembros
from tests.factories.base import commit_and_refresh

def adicionar_membro_empresa(db, empresa_id, usuario_id, papel="admin"):
    membro = EmpresaMembros(
        empresa_id=empresa_id,
        usuario_id=usuario_id,
        papel=papel,
    )
    return commit_and_refresh(db, membro)
