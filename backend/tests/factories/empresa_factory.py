"""
Empresa factory for tests.

DEPRECATED: Empresas are now managed by the Auth microservice.
This factory now creates mock empresa data for testing purposes.
The empresa_id is a UUID that would be provided by the Auth service.
"""

import uuid


def criar_empresa_mock(
    razao_social="Empresa Teste LTDA",
    fantasia="Empresa Teste",
    cnpj="12345678000199",
    timezone="America/Sao_Paulo",
):
    """
    Create mock empresa data for testing.

    This returns a dict representing empresa data as it would be received
    from the Auth service.
    """
    return {
        "empresa_id": str(uuid.uuid4()),
        "razao_social": razao_social,
        "fantasia": fantasia,
        "cnpj": cnpj,
        "timezone": timezone,
    }


def get_mock_empresa_id():
    """Generate a mock empresa UUID for testing."""
    return str(uuid.uuid4())


class MockEmpresa:
    """
    Mock empresa object for backward compatibility with old tests.

    DEPRECATED: This is a temporary compatibility layer for tests that
    still expect an empresa object. New tests should use criar_empresa_mock()
    or get_mock_empresa_id() instead.
    """
    def __init__(
        self,
        empresa_id,
        razao_social="Empresa Teste LTDA",
        fantasia="Empresa Teste",
        cnpj="12345678000199",
        timezone="America/Sao_Paulo",
        usuario_id=None
    ):
        self.empresa_id = empresa_id
        self.razao_social = razao_social
        self.fantasia = fantasia
        self.cnpj = cnpj
        self.timezone = timezone
        self.usuario_id = usuario_id


def criar_empresa(
    db_session=None,
    usuario_id=None,
    razao_social="Empresa Teste LTDA",
    fantasia="Empresa Teste",
    cnpj="12345678000199",
    timezone="America/Sao_Paulo"
):
    """
    Create a mock empresa for backward compatibility.

    DEPRECATED: This function exists for backward compatibility with old tests.
    New tests should use the Auth service mocks instead.

    Note: The db_session parameter is ignored as empresas are no longer stored locally.
    """
    empresa_id = str(uuid.uuid4())
    return MockEmpresa(
        empresa_id=empresa_id,
        razao_social=razao_social,
        fantasia=fantasia,
        cnpj=cnpj,
        timezone=timezone,
        usuario_id=usuario_id
    )
