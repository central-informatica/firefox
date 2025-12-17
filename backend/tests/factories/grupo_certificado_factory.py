from backend.app.db.models import GruposCertificados
from tests.factories.base import commit_and_refresh

def vincular_certificado_ao_grupo(db, empresa_id: int, grupo_id: int, certificado_id: int):
    gc = GruposCertificados(
        empresa_id=empresa_id,
        grupo_id=grupo_id,
        certificado_id=certificado_id,
    )
    return commit_and_refresh(db, gc)
