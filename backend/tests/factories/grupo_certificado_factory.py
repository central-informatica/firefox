from backend.app.db.models import GruposCertificados
from tests.factories.base import commit_and_refresh

def vincular_certificado_ao_grupo(db, empresa_id: str, grupo_id: str, certificado_id: str):
    gc = GruposCertificados(
        empresa_id=empresa_id,
        grupo_id=grupo_id,
        certificado_id=certificado_id,
    )
    return commit_and_refresh(db, gc)
