"""Factory for creating GruposCertificadosUrls test data."""

from backend.app.db.models import GruposCertificadosUrls
from tests.factories.base import commit_and_refresh


def criar_grupos_certificados_urls(db, grupo_cert_id, global_urls_id, empresa_id):
    """Create a test grupo-certificado URL association."""
    entry = GruposCertificadosUrls(
        grupo_cert_id=grupo_cert_id,
        global_urls_id=global_urls_id,
        empresa_id=empresa_id,
    )
    return commit_and_refresh(db, entry)
