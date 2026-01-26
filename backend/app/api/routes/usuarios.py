"""
User management routes - proxies to Auth microservice.

All user CRUD operations are delegated to the Auth service (port 8001).
Admin-only access with IP whitelist validation.
"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel

from backend.app.api.deps import check_auth_with_ip
from backend.app.core.exceptions import AuthServiceError
from backend.app.services.auth_client import auth_client

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

# Headers to exclude when forwarding
EXCLUDED_HEADERS = {'content-length', 'host', 'transfer-encoding', 'content-type'}


def get_forwarded_headers(request: Request) -> dict[str, str]:
    """Extract headers to forward, excluding hop-by-hop and body-related headers."""
    return {
        k: v for k, v in request.headers.items()
        if k.lower() not in EXCLUDED_HEADERS
    }


# -----------------------------------------------------------------------------
# Request/Response Models
# -----------------------------------------------------------------------------


class UserUpdate(BaseModel):
    """User update request."""

    first_name: str | None = None
    last_name: str | None = None
    is_active: bool | None = None
    requires_2fa: bool | None = None


# -----------------------------------------------------------------------------
# Routes
# -----------------------------------------------------------------------------


@router.get("/")
async def list_users(
    request: Request,
    organization_id: str | None = None,
    include_deleted: bool = False,
    limit: int = 100,
    offset: int = 0,
    user_data: dict[str, Any] = Depends(check_auth_with_ip),
) -> Any:
    """
    List users in organization.

    Admin only - Forwards request to Auth service /api/v1/users/.
    """
    # Check if user is admin
    if not user_data.get("is_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas administradores podem listar usuários",
        )

    headers = get_forwarded_headers(request)

    params = {
        "limit": limit,
        "offset": offset,
        "include_deleted": str(include_deleted).lower(),
    }
    if organization_id:
        params["organization_id"] = organization_id

    try:
        return await auth_client.proxy_request(
            method="GET",
            path="/api/v1/users/",
            headers=headers,
            params=params,
        )

    except AuthServiceError as e:
        raise HTTPException(
            status_code=e.status_code or 500,
            detail=e.message,
        )


@router.get("/{user_id}")
async def get_user(
    request: Request,
    user_id: str,
    user_data: dict[str, Any] = Depends(check_auth_with_ip),
) -> Any:
    """
    Get specific user by ID.

    Admin only - Forwards request to Auth service /api/v1/users/{user_id}.
    """
    # Check if user is admin
    if not user_data.get("is_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas administradores podem visualizar usuários",
        )

    headers = get_forwarded_headers(request)

    try:
        return await auth_client.proxy_request(
            method="GET",
            path=f"/api/v1/users/{user_id}",
            headers=headers,
        )

    except AuthServiceError as e:
        raise HTTPException(
            status_code=e.status_code or 500,
            detail=e.message,
        )


@router.put("/{user_id}")
async def update_user(
    request: Request,
    user_id: str,
    data: UserUpdate,
    user_data: dict[str, Any] = Depends(check_auth_with_ip),
) -> Any:
    """
    Update user.

    Admin only - Forwards request to Auth service /api/v1/users/{user_id}.
    """
    # Check if user is admin
    if not user_data.get("is_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas administradores podem atualizar usuários",
        )

    headers = get_forwarded_headers(request)
    update_data = data.model_dump(exclude_none=True)

    try:
        return await auth_client.proxy_request(
            method="PUT",
            path=f"/api/v1/users/{user_id}",
            headers=headers,
            json=update_data,
        )

    except AuthServiceError as e:
        raise HTTPException(
            status_code=e.status_code or 500,
            detail=e.message,
        )


@router.delete("/{user_id}")
async def delete_user(
    request: Request,
    user_id: str,
    user_data: dict[str, Any] = Depends(check_auth_with_ip),
) -> Any:
    """
    Soft delete user.

    Admin only - Forwards request to Auth service /api/v1/users/{user_id}.
    """
    # Check if user is admin
    if not user_data.get("is_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas administradores podem remover usuários",
        )

    headers = get_forwarded_headers(request)

    try:
        return await auth_client.proxy_request(
            method="DELETE",
            path=f"/api/v1/users/{user_id}",
            headers=headers,
        )

    except AuthServiceError as e:
        raise HTTPException(
            status_code=e.status_code or 500,
            detail=e.message,
        )
