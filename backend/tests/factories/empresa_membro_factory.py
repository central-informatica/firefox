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


class MockEmpresaMembro:
    """
    Mock empresa membro object for backward compatibility with old tests.

    DEPRECATED: This is a temporary compatibility layer for tests that
    still expect an empresa membro object.
    """
    def __init__(self, membro_id, empresa_id, usuario_id, papel="COMUM"):
        self.membro_id = membro_id
        self.empresa_id = empresa_id
        self.usuario_id = usuario_id
        self.papel = papel


def adicionar_membro_empresa(db_session=None, empresa_id=None, usuario_id=None, papel="COMUM"):
    """
    Add a mock empresa membro for backward compatibility.

    DEPRECATED: This function exists for backward compatibility with old tests.
    New tests should use the Auth service mocks instead.

    Note: The db_session parameter is ignored as memberships are no longer stored locally.
    """
    membro_id = str(uuid.uuid4())
    return MockEmpresaMembro(
        membro_id=membro_id,
        empresa_id=empresa_id or str(uuid.uuid4()),
        usuario_id=usuario_id or str(uuid.uuid4()),
        papel=papel
    )
