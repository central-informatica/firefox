"""
User management routes - proxies to Auth microservice.

All user CRUD operations are delegated to the Auth service (port 8001).
Admin-only access with IP whitelist validation.
"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
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


class UserCreate(BaseModel):
    """User creation request (sends invitation)."""

    nome: str
    email: str
    nivel: str = "COMUM"
    empresa_id: str | None = None


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


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(
    request: Request,
    data: UserCreate,
    user_data: dict[str, Any] = Depends(check_auth_with_ip),
) -> Any:
    """
    Create a new user by sending an invitation.

    Admin only - Creates an invitation via Auth service /api/v1/invitations/.
    The invited user will receive an email with instructions to complete registration.
    """
    # Check if user is admin
    if not user_data.get("is_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas administradores podem criar usuários",
        )

    headers = get_forwarded_headers(request)

    # Add Authorization header from session_token cookie
    session_token = request.cookies.get("session_token")
    if session_token:
        headers["Authorization"] = f"Bearer {session_token}"

    # Split nome into first_name and last_name
    name_parts = data.nome.strip().split(" ", 1)
    first_name = name_parts[0] if name_parts else ""
    last_name = name_parts[1] if len(name_parts) > 1 else ""

    invitation_data = {
        "email": data.email,
        "first_name": first_name,
        "last_name": last_name,
    }

    # Add company_id if provided
    if data.empresa_id:
        invitation_data["company_id"] = data.empresa_id

    try:
        return await auth_client.proxy_request(
            method="POST",
            path="/api/v1/invitations/",
            headers=headers,
            json=invitation_data,
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

    # Add Authorization header from session_token cookie
    session_token = request.cookies.get("session_token")
    if session_token:
        headers["Authorization"] = f"Bearer {session_token}"

    try:
        result = await auth_client.proxy_request(
            method="GET",
            path=f"/api/v1/users/{user_id}",
            headers=headers,
        )

        # Transform response to frontend expected format
        first_name = result.get("first_name", "") or ""
        last_name = result.get("last_name", "") or ""
        nome = f"{first_name} {last_name}".strip()

        return {
            "id": result.get("id"),
            "nome": nome,
            "email": result.get("email"),
            "nivel": "ADMINISTRADOR" if result.get("is_admin") else "COMUM",
            "is_active": result.get("is_active", True),
            "first_name": first_name,
            "last_name": last_name,
        }

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


@router.get("/empresas/{empresa_id}/usuarios")
async def list_users_by_company(
    request: Request,
    empresa_id: str,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    search: str = "",
    sort: str = "",
    user_data: dict[str, Any] = Depends(check_auth_with_ip),
) -> Any:
    """
    List users that belong to a specific company.

    Admin only - Forwards request to Auth service /api/v1/companies/{company_id}/users.
    """
    # Check if user is admin
    if not user_data.get("is_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas administradores podem listar usuários por empresa",
        )

    headers = get_forwarded_headers(request)

    # Add Authorization header from session_token cookie
    session_token = request.cookies.get("session_token")
    if session_token:
        headers["Authorization"] = f"Bearer {session_token}"

    try:
        result = await auth_client.proxy_request(
            method="GET",
            path=f"/api/v1/companies/{empresa_id}/users",
            headers=headers,
        )

        # Auth service returns a list of users directly
        users = result if isinstance(result, list) else []

        # Apply search filter if provided
        if search:
            search_lower = search.lower()
            users = [
                u for u in users
                if search_lower in (u.get("email", "") or "").lower()
                or search_lower in (u.get("first_name", "") or "").lower()
                or search_lower in (u.get("last_name", "") or "").lower()
            ]

        total = len(users)

        # Apply pagination
        offset = (page - 1) * limit
        paginated_users = users[offset:offset + limit]

        # Transform to frontend expected format
        data = [
            {
                "id": u.get("user_id"),
                "nome": f"{u.get('first_name', '')} {u.get('last_name', '')}".strip(),
                "email": u.get("email"),
                "is_active": u.get("is_active", True),
                "is_admin": u.get("is_admin", False),
                "added_at": u.get("added_at"),
            }
            for u in paginated_users
        ]

        return {
            "data": data,
            "total": total,
        }

    except AuthServiceError as e:
        raise HTTPException(
            status_code=e.status_code or 500,
            detail=e.message,
        )
