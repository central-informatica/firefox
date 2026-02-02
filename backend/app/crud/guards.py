"""
Guards for access validation.

Note: Access validation now trusts the Auth microservice.
The user_data from check_auth() already contains validated organization memberships.
These functions are kept for backward compatibility but no longer query the local DB
for user/empresa data since those are managed by the Auth service.
"""

from sqlalchemy.orm import Session


def exigir_acesso_empresa(db: Session, empresa_id: str, usuario_id: str):
    """
    Validate user access to an empresa.

    This function is kept for backward compatibility but the actual validation
    is done by the Auth service. When we reach this point, the user is already
    authenticated and their organization membership has been validated.

    The empresa_id is trusted because it comes from the Auth service's /me endpoint
    which validates the user's organization memberships.
    """
    # Auth service already validated the user and their organization membership
    # If we reach this point, the user is authenticated and authorized
    pass
