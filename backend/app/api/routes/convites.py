"""
Invitation management routes - proxies to Auth microservice.

All invitation operations are delegated to the Auth service (port 8001).
Admin-only access with IP whitelist validation (except accept endpoint).
"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, EmailStr

from backend.app.api.deps import check_auth_with_ip
from backend.app.core.exceptions import AuthServiceError
from backend.app.services.auth_client import auth_client

router = APIRouter(prefix="/convites", tags=["Convites"])

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


class InviteUserRequest(BaseModel):
    """Invite user to organization request."""

    email: EmailStr


class AcceptInvitationRequest(BaseModel):
    """Accept invitation request."""

    token: str
    password: str
    first_name: str
    last_name: str





# -----------------------------------------------------------------------------
# Routes
# -----------------------------------------------------------------------------


@router.post("/")
async def create_invitation(
    request: Request,
    data: InviteUserRequest,
    user_data: dict[str, Any] = Depends(check_auth_with_ip),
) -> Any:
    """
    Create invitation to join organization.

    Admin only - Forwards request to Auth service /api/v1/invitations/.
    """
    # Check if user is admin
    if not user_data.get("is_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas administradores podem criar convites",
        )

    headers = get_forwarded_headers(request)

    try:
        return await auth_client.proxy_request(
            method="POST",
            path="/api/v1/invitations/",
            headers=headers,
            json={"email": data.email},
        )

    except AuthServiceError as e:
        raise HTTPException(
            status_code=e.status_code or 500,
            detail=e.message,
        )


@router.get("/")
async def list_invitations(
    request: Request,
    include_accepted: bool = False,
    limit: int = 100,
    offset: int = 0,
    user_data: dict[str, Any] = Depends(check_auth_with_ip),
) -> Any:
    """
    List invitations for current organization.

    Admin only - Forwards request to Auth service /api/v1/invitations/.
    """
    # Check if user is admin
    if not user_data.get("is_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas administradores podem listar convites",
        )

    headers = get_forwarded_headers(request)

    params = {
        "include_accepted": include_accepted,
        "limit": limit,
        "offset": offset,
    }

    try:
        return await auth_client.proxy_request(
            method="GET",
            path="/api/v1/invitations/",
            headers=headers,
            params=params,
        )

    except AuthServiceError as e:
        raise HTTPException(
            status_code=e.status_code or 500,
            detail=e.message,
        )


@router.delete("/{invitation_id}")
async def revoke_invitation(
    request: Request,
    invitation_id: str,
    user_data: dict[str, Any] = Depends(check_auth_with_ip),
) -> Any:
    """
    Revoke a pending invitation.

    Admin only - Forwards request to Auth service /api/v1/invitations/{invitation_id}.
    """
    # Check if user is admin
    if not user_data.get("is_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas administradores podem revogar convites",
        )

    headers = get_forwarded_headers(request)

    try:
        return await auth_client.proxy_request(
            method="DELETE",
            path=f"/api/v1/invitations/{invitation_id}",
            headers=headers,
        )

    except AuthServiceError as e:
        raise HTTPException(
            status_code=e.status_code or 500,
            detail=e.message,
        )


@router.post("/accept")
async def accept_invitation(
    request: Request,
    data: AcceptInvitationRequest,
) -> Any:
    """
    Accept an invitation to join organization.

    Forwards request to Auth service /api/v1/invitations/accept.
    """
    headers = get_forwarded_headers(request)

    try:
        return await auth_client.proxy_request(
            method="POST",
            path="/api/v1/invitations/accept",
            headers=headers,
            json=data.model_dump(),
        )

    except AuthServiceError as e:
        raise HTTPException(
            status_code=e.status_code or 500,
            detail=e.message,
        )
