"""Factory for creating UsuariosIpWhitelist test data."""

from backend.app.db.models import UsuariosIpWhitelist
from tests.factories.base import commit_and_refresh


def criar_usuarios_ip_whitelist(
    db,
    usuario_id,
    empresa_id,
    ip_address="192.168.1.100",
    descricao=None,
    criado_por=None,
):
    """Create a test IP whitelist entry."""
    entry = UsuariosIpWhitelist(
        usuario_id=usuario_id,
        empresa_id=empresa_id,
        ip_address=ip_address,
        descricao=descricao,
        criado_por=criado_por or usuario_id,
    )
    return commit_and_refresh(db, entry)
