"""
Security module for authentication and authorization.

This module delegates authentication to the Auth microservice (port 8001).
All session validation is performed by calling the Auth service's /auth/me endpoint.
"""

from typing import Any, Optional

from fastapi import HTTPException, Request, status

from backend.app.services.auth_client import auth_client


async def validar_token(request: Request) -> dict[str, Any]:
    """
    Validate session by calling the Auth microservice.

    This function:
    1. Extracts session_token from HttpOnly cookie
    2. Optionally extracts CSRF token from header
    3. Calls Auth service to validate and get user info

    Returns:
        dict with user information from Auth service:
        - id: User ID
        - email: User email
        - first_name, last_name: User name
        - organization_id: Current organization ID
        - is_owner: Whether user owns the organization
        - requires_2fa: Whether 2FA is required/verified

    Raises:
        HTTPException 401: If session is missing or invalid
    """
    # 1. Extract session token from cookie
    session_token = request.cookies.get("session_token")
    if not session_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sessao ausente",
        )

    # 2. Extract CSRF token from header (optional for GET requests)
    csrf_token = request.headers.get("X-CSRF-Token")

    # 3. Validate with Auth service
    try:
        user_data = await auth_client.get_current_user(
            session_token=session_token,
            csrf_token=csrf_token,
        )
    except Exception as e:
        # Log the error but don't expose internal details
        import logging

        logging.getLogger(__name__).error(f"Auth service error: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Servico de autenticacao indisponivel",
        )

    if user_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sessao invalida ou expirada",
        )

    return user_data


def get_user_id(user_data: dict[str, Any]) -> int:
    """
    Extract user ID from Auth service response.

    Args:
        user_data: User data dict from validar_token

    Returns:
        User ID as integer
    """
    return user_data.get("id") or user_data.get("usuario_id")


def get_organization_id(user_data: dict[str, Any]) -> Optional[int]:
    """
    Extract organization ID from Auth service response.

    Args:
        user_data: User data dict from validar_token

    Returns:
        Organization ID or None
    """
    return user_data.get("organization_id")


def is_organization_owner(user_data: dict[str, Any]) -> bool:
    """
    Check if user is owner of their organization.

    Args:
        user_data: User data dict from validar_token

    Returns:
        True if user is organization owner
    """
    return user_data.get("is_owner", False)
