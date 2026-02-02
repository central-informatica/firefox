"""
EmpresaMembro factory for tests.

DEPRECATED: EmpresaMembros are now managed by the Auth microservice.
This factory now creates mock membership data for testing purposes.
"""

import uuid


def criar_membro_mock(empresa_id=None, usuario_id=None, papel="COMUM"):
    """
    Create mock empresa membership data for testing.

    This returns a dict representing membership data as it would be received
    from the Auth service.
    """
    return {
        "membro_id": str(uuid.uuid4()),
        "empresa_id": empresa_id or str(uuid.uuid4()),
        "usuario_id": usuario_id or str(uuid.uuid4()),
        "papel": papel,
    }
