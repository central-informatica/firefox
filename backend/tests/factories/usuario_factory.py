"""
Usuario factory for tests.

DEPRECATED: Usuarios are now managed by the Auth microservice.
This factory now creates mock usuario data for testing purposes.
The usuario_id is a UUID that would be provided by the Auth service.
"""

import uuid


def criar_usuario_mock(
    nome="Admin",
    email="admin@test.com",
    nivel="COMUM",
):
    """
    Create mock usuario data for testing.

    This returns a dict representing user data as it would be received
    from the Auth service's /me endpoint.
    """
    return {
        "usuario_id": str(uuid.uuid4()),
        "nome": nome,
        "email": email,
        "nivel": nivel,
        "email_verificado": True,
    }


def get_mock_usuario_id():
    """Generate a mock usuario UUID for testing."""
    return str(uuid.uuid4())
