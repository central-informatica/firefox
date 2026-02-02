from backend.app.db.models import GruposUsuarios
from tests.factories.base import commit_and_refresh

def adicionar_usuario_ao_grupo(db, empresa_id, grupo_id, usuario_id):
    vinculo = GruposUsuarios(
        empresa_id=empresa_id,
        grupo_id=grupo_id,
        usuario_id=usuario_id,
    )
    return commit_and_refresh(db, vinculo)
