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
