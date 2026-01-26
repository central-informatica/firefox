"""
Company management routes - proxies to Auth microservice.

All company CRUD operations are delegated to the Auth service (port 8001).
Admin-only access with IP whitelist validation (except user's own companies endpoint).
"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel

from backend.app.api.deps import check_auth_with_ip, get_user_id_from_data
from backend.app.core.exceptions import AuthServiceError
from backend.app.services.auth_client import auth_client

router = APIRouter(prefix="/companies", tags=["Companies"])

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


class CompanyCreate(BaseModel):
    """Company creation request."""

    name: str
    cnpj: str | None = None
    description: str | None = None


class CompanyUpdate(BaseModel):
    """Company update request."""

    name: str | None = None
    cnpj: str | None = None
    description: str | None = None


class CompanyUserAssignment(BaseModel):
    """Assign user to company request."""

    user_id: str
    role: str | None = None


# -----------------------------------------------------------------------------
# Routes - Organization-level Company Management
# -----------------------------------------------------------------------------


@router.get("/organizations/{org_id}/companies")
async def list_companies(
    request: Request,
    org_id: str,
    limit: int = 100,
    offset: int = 0,
    include_deleted: bool = False,
    user_data: dict[str, Any] = Depends(check_auth_with_ip),
) -> Any:
    """
    List companies in organization.

    Admin only - Forwards request to Auth service /api/v1/organizations/{org_id}/companies.
    """
    # Check if user is admin
    if not user_data.get("is_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas administradores podem listar empresas",
        )

    headers = get_forwarded_headers(request)

    params = {
        "limit": limit,
        "offset": offset,
        "include_deleted": str(include_deleted).lower(),
    }

    try:
        return await auth_client.proxy_request(
            method="GET",
            path=f"/api/v1/organizations/{org_id}/companies",
            headers=headers,
            params=params,
        )

    except AuthServiceError as e:
        raise HTTPException(
            status_code=e.status_code or 500,
            detail=e.message,
        )


@router.get("/organizations/{org_id}/companies/{company_id}")
async def get_company(
    request: Request,
    org_id: str,
    company_id: str,
    user_data: dict[str, Any] = Depends(check_auth_with_ip),
) -> Any:
    """
    Get specific company by ID.

    Admin only - Forwards request to Auth service /api/v1/organizations/{org_id}/companies/{company_id}.
    """
    # Check if user is admin
    if not user_data.get("is_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas administradores podem visualizar empresas",
        )

    headers = get_forwarded_headers(request)

    try:
        return await auth_client.proxy_request(
            method="GET",
            path=f"/api/v1/organizations/{org_id}/companies/{company_id}",
            headers=headers,
        )

    except AuthServiceError as e:
        raise HTTPException(
            status_code=e.status_code or 500,
            detail=e.message,
        )


@router.post("/organizations/{org_id}/companies")
async def create_company(
    request: Request,
    org_id: str,
    data: CompanyCreate,
    user_data: dict[str, Any] = Depends(check_auth_with_ip),
) -> Any:
    """
    Create company in organization.

    Admin only - Forwards request to Auth service /api/v1/organizations/{org_id}/companies.
    """
    # Check if user is admin
    if not user_data.get("is_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas administradores podem criar empresas",
        )

    headers = get_forwarded_headers(request)
    company_data = data.model_dump(exclude_none=True)

    try:
        return await auth_client.proxy_request(
            method="POST",
            path=f"/api/v1/organizations/{org_id}/companies",
            headers=headers,
            json=company_data,
        )

    except AuthServiceError as e:
        raise HTTPException(
            status_code=e.status_code or 500,
            detail=e.message,
        )


@router.put("/organizations/{org_id}/companies/{company_id}")
async def update_company(
    request: Request,
    org_id: str,
    company_id: str,
    data: CompanyUpdate,
    user_data: dict[str, Any] = Depends(check_auth_with_ip),
) -> Any:
    """
    Update company.

    Admin only - Forwards request to Auth service /api/v1/organizations/{org_id}/companies/{company_id}.
    """
    # Check if user is admin
    if not user_data.get("is_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas administradores podem atualizar empresas",
        )

    headers = get_forwarded_headers(request)
    update_data = data.model_dump(exclude_none=True)

    try:
        return await auth_client.proxy_request(
            method="PUT",
            path=f"/api/v1/organizations/{org_id}/companies/{company_id}",
            headers=headers,
            json=update_data,
        )

    except AuthServiceError as e:
        raise HTTPException(
            status_code=e.status_code or 500,
            detail=e.message,
        )


@router.delete("/organizations/{org_id}/companies/{company_id}")
async def delete_company(
    request: Request,
    org_id: str,
    company_id: str,
    user_data: dict[str, Any] = Depends(check_auth_with_ip),
) -> Any:
    """
    Delete company.

    Admin only - Forwards request to Auth service /api/v1/organizations/{org_id}/companies/{company_id}.
    """
    # Check if user is admin
    if not user_data.get("is_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas administradores podem remover empresas",
        )

    headers = get_forwarded_headers(request)

    try:
        return await auth_client.proxy_request(
            method="DELETE",
            path=f"/api/v1/organizations/{org_id}/companies/{company_id}",
            headers=headers,
        )

    except AuthServiceError as e:
        raise HTTPException(
            status_code=e.status_code or 500,
            detail=e.message,
        )


# -----------------------------------------------------------------------------
# Routes - Company-level User Management
# -----------------------------------------------------------------------------


@router.get("/{company_id}/users")
async def list_company_users(
    request: Request,
    company_id: str,
    limit: int = 100,
    offset: int = 0,
    user_data: dict[str, Any] = Depends(check_auth_with_ip),
) -> Any:
    """
    List users in company.

    Admin only - Forwards request to Auth service /api/v1/companies/{company_id}/users.
    """
    # Check if user is admin
    if not user_data.get("is_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas administradores podem listar usuários da empresa",
        )

    headers = get_forwarded_headers(request)

    params = {
        "limit": limit,
        "offset": offset,
    }

    try:
        return await auth_client.proxy_request(
            method="GET",
            path=f"/api/v1/companies/{company_id}/users",
            headers=headers,
            params=params,
        )

    except AuthServiceError as e:
        raise HTTPException(
            status_code=e.status_code or 500,
            detail=e.message,
        )


@router.post("/{company_id}/users")
async def add_user_to_company(
    request: Request,
    company_id: str,
    data: CompanyUserAssignment,
    user_data: dict[str, Any] = Depends(check_auth_with_ip),
) -> Any:
    """
    Add user to company.

    Admin only - Forwards request to Auth service /api/v1/companies/{company_id}/users.
    """
    # Check if user is admin
    if not user_data.get("is_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas administradores podem adicionar usuários à empresa",
        )

    headers = get_forwarded_headers(request)
    assignment_data = data.model_dump(exclude_none=True)

    try:
        return await auth_client.proxy_request(
            method="POST",
            path=f"/api/v1/companies/{company_id}/users",
            headers=headers,
            json=assignment_data,
        )

    except AuthServiceError as e:
        raise HTTPException(
            status_code=e.status_code or 500,
            detail=e.message,
        )


@router.delete("/{company_id}/users/{user_id}")
async def remove_user_from_company(
    request: Request,
    company_id: str,
    user_id: str,
    user_data: dict[str, Any] = Depends(check_auth_with_ip),
) -> Any:
    """
    Remove user from company.

    Admin only - Forwards request to Auth service /api/v1/companies/{company_id}/users/{user_id}.
    """
    # Check if user is admin
    if not user_data.get("is_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas administradores podem remover usuários da empresa",
        )

    headers = get_forwarded_headers(request)

    try:
        return await auth_client.proxy_request(
            method="DELETE",
            path=f"/api/v1/companies/{company_id}/users/{user_id}",
            headers=headers,
        )

    except AuthServiceError as e:
        raise HTTPException(
            status_code=e.status_code or 500,
            detail=e.message,
        )


# -----------------------------------------------------------------------------
# Routes - User-level Company Access
# -----------------------------------------------------------------------------


@router.get("/users/{user_id}/companies")
async def list_user_companies(
    request: Request,
    user_id: str,
    limit: int = 100,
    offset: int = 0,
    user_data: dict[str, Any] = Depends(check_auth_with_ip),
) -> Any:
    """
    List user's companies.

    Accessible by admin or the user themselves.
    Forwards request to Auth service /api/v1/users/{user_id}/companies.
    """
    # Check if user is admin or the user themselves
    current_user_id = get_user_id_from_data(user_data)
    is_admin = user_data.get("is_admin")

    if not is_admin and str(current_user_id) != str(user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para visualizar as empresas deste usuário",
        )

    headers = get_forwarded_headers(request)

    params = {
        "limit": limit,
        "offset": offset,
    }

    try:
        return await auth_client.proxy_request(
            method="GET",
            path=f"/api/v1/users/{user_id}/companies",
            headers=headers,
            params=params,
        )

    except AuthServiceError as e:
        raise HTTPException(
            status_code=e.status_code or 500,
            detail=e.message,
        )
