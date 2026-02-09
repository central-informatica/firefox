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


class MockUsuario:
    """
    Mock usuario object for backward compatibility with old tests.

    DEPRECATED: This is a temporary compatibility layer for tests that
    still expect a usuario object. New tests should use criar_usuario_mock()
    or get_mock_usuario_id() instead.
    """
    def __init__(self, usuario_id, nome="Admin", email="admin@test.com", nivel="COMUM"):
        self.usuario_id = usuario_id
        self.nome = nome
        self.email = email
        self.nivel = nivel
        self.email_verificado = True


def criar_usuario(db_session=None, nome="Admin", email="admin@test.com", nivel="COMUM"):
    """
    Create a mock usuario for backward compatibility.

    DEPRECATED: This function exists for backward compatibility with old tests.
    New tests should use the Auth service mocks instead.

    Note: The db_session parameter is ignored as usuarios are no longer stored locally.
    """
    usuario_id = str(uuid.uuid4())
    return MockUsuario(
        usuario_id=usuario_id,
        nome=nome,
        email=email,
        nivel=nivel
    )
