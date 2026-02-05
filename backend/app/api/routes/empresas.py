"""
Empresas (Companies) routes - proxies to Auth microservice.

Simplified endpoints that use the user's organization from auth context.
"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.app.api.deps import check_auth_with_ip
from backend.app.core.exceptions import AuthServiceError
from backend.app.db.session import get_db
from backend.app.db.models import Certificados
from backend.app.services.auth_client import auth_client

router = APIRouter(prefix="/empresas", tags=["Empresas"])

# Headers to exclude when forwarding
EXCLUDED_HEADERS = {'content-length', 'host', 'transfer-encoding', 'content-type'}


def get_forwarded_headers(request: Request) -> dict[str, str]:
    """Extract headers to forward, excluding hop-by-hop and body-related headers.

    Also adds Authorization header from session_token cookie if present.
    """
    headers = {
        k: v for k, v in request.headers.items()
        if k.lower() not in EXCLUDED_HEADERS
    }

    # Add Authorization header from session_token cookie
    session_token = request.cookies.get("session_token")
    if session_token:
        headers["Authorization"] = f"Bearer {session_token}"

    return headers


class EmpresaCreate(BaseModel):
    """Empresa creation request."""
    name: str
    cnpj: str
    timezone: str = "America/Sao_Paulo"
    category_id: str | None = None


class EmpresaUpdate(BaseModel):
    """Empresa update request."""
    name: str | None = None
    cnpj: str | None = None
    timezone: str | None = None
    category_id: str | None = None


@router.get("/")
async def listar_empresas(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    search: str = "",
    sort: str = "",
    user_data: dict[str, Any] = Depends(check_auth_with_ip),
) -> Any:
    """
    List companies in the user's organization with pagination.
    """
    if not user_data.get("is_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas administradores podem listar empresas",
        )

    org_id = user_data.get("organization_id")
    if not org_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuário não está associado a uma organização",
        )

    headers = get_forwarded_headers(request)
    params = {
        "limit": limit,
        "offset": (page - 1) * limit,
    }
    if search:
        params["search"] = search

    try:
        result = await auth_client.proxy_request(
            method="GET",
            path=f"/api/v1/organizations/{org_id}/companies",
            headers=headers,
            params=params,
        )

        # Adapta resposta para o formato esperado pelo frontend
        companies = result if isinstance(result, list) else result.get("companies", [])
        total = result.get("total", len(companies)) if isinstance(result, dict) else len(companies)

        return {
            "data": companies,
            "total": total,
        }

    except AuthServiceError as e:
        raise HTTPException(
            status_code=e.status_code or 500,
            detail=e.message,
        )


@router.get("/minhas")
async def listar_minhas_empresas(
    request: Request,
    user_data: dict[str, Any] = Depends(check_auth_with_ip),
) -> Any:
    """
    List companies the current user has access to.

    For admins: returns ALL companies in their organization.
    For regular users: returns only companies they are assigned to.
    """
    headers = get_forwarded_headers(request)

    # Admins see all companies in their organization
    if user_data.get("is_admin"):
        org_id = user_data.get("organization_id")
        if not org_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Usuário não está associado a uma organização",
            )

        try:
            result = await auth_client.proxy_request(
                method="GET",
                path=f"/api/v1/organizations/{org_id}/companies",
                headers=headers,
                params={"limit": 100, "offset": 0},
            )
            # Return companies array from the response
            if isinstance(result, dict) and "companies" in result:
                return result["companies"]
            return result if isinstance(result, list) else []

        except AuthServiceError as e:
            raise HTTPException(
                status_code=e.status_code or 500,
                detail=e.message,
            )

    # Regular users see only assigned companies
    user_id = user_data.get("id") or user_data.get("usuario_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID do usuário não encontrado",
        )

    try:
        return await auth_client.proxy_request(
            method="GET",
            path=f"/api/v1/users/{user_id}/companies",
            headers=headers,
        )

    except AuthServiceError as e:
        raise HTTPException(
            status_code=e.status_code or 500,
            detail=e.message,
        )


@router.get("/id/{empresa_id}")
async def get_empresa(
    request: Request,
    empresa_id: str,
    user_data: dict[str, Any] = Depends(check_auth_with_ip),
) -> Any:
    """
    Get a specific company by ID.
    """
    if not user_data.get("is_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas administradores podem visualizar empresas",
        )

    org_id = user_data.get("organization_id")
    if not org_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuário não está associado a uma organização",
        )

    headers = get_forwarded_headers(request)

    try:
        return await auth_client.proxy_request(
            method="GET",
            path=f"/api/v1/organizations/{org_id}/companies/{empresa_id}",
            headers=headers,
        )

    except AuthServiceError as e:
        raise HTTPException(
            status_code=e.status_code or 500,
            detail=e.message,
        )


@router.post("/")
async def criar_empresa(
    request: Request,
    data: EmpresaCreate,
    user_data: dict[str, Any] = Depends(check_auth_with_ip),
) -> Any:
    """
    Create a new company.
    """
    if not user_data.get("is_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas administradores podem criar empresas",
        )

    org_id = user_data.get("organization_id")
    if not org_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuário não está associado a uma organização",
        )

    headers = get_forwarded_headers(request)

    # Build company data for Auth service
    # Auth service model expects company_category_id directly
    company_data = {
        "name": data.name,
        "cnpj": data.cnpj,
        "timezone": data.timezone,
        "company_category_id": data.category_id,
    }

    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"[EMPRESAS] Creating company with data: {company_data}")
    logger.info(f"[EMPRESAS] org_id: {org_id}")

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


@router.put("/id/{empresa_id}")
async def atualizar_empresa(
    request: Request,
    empresa_id: str,
    data: EmpresaUpdate,
    user_data: dict[str, Any] = Depends(check_auth_with_ip),
) -> Any:
    """
    Update an existing company.
    """
    if not user_data.get("is_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas administradores podem atualizar empresas",
        )

    org_id = user_data.get("organization_id")
    if not org_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuário não está associado a uma organização",
        )

    headers = get_forwarded_headers(request)

    # Build update data for Auth service
    update_data = {}
    if data.name is not None:
        update_data["name"] = data.name
    if data.cnpj is not None:
        update_data["cnpj"] = data.cnpj
    if data.timezone is not None:
        update_data["timezone"] = data.timezone
    if data.category_id is not None:
        update_data["company_category_id"] = data.category_id

    try:
        return await auth_client.proxy_request(
            method="PUT",
            path=f"/api/v1/organizations/{org_id}/companies/{empresa_id}",
            headers=headers,
            json=update_data,
        )

    except AuthServiceError as e:
        raise HTTPException(
            status_code=e.status_code or 500,
            detail=e.message,
        )


@router.delete("/id/{empresa_id}")
async def deletar_empresa(
    request: Request,
    empresa_id: str,
    user_data: dict[str, Any] = Depends(check_auth_with_ip),
) -> Any:
    """
    Delete a company.
    """
    if not user_data.get("is_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas administradores podem remover empresas",
        )

    org_id = user_data.get("organization_id")
    if not org_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuário não está associado a uma organização",
        )

    headers = get_forwarded_headers(request)

    try:
        return await auth_client.proxy_request(
            method="DELETE",
            path=f"/api/v1/organizations/{org_id}/companies/{empresa_id}",
            headers=headers,
        )

    except AuthServiceError as e:
        raise HTTPException(
            status_code=e.status_code or 500,
            detail=e.message,
        )


@router.get("/id/{empresa_id}/status")
async def get_empresa_status(
    request: Request,
    empresa_id: str,
    user_data: dict[str, Any] = Depends(check_auth_with_ip),
) -> Any:
    """
    Get the active status of a company from Auth service.
    """
    if not user_data.get("is_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas administradores podem verificar status de empresas",
        )

    org_id = user_data.get("organization_id")
    if not org_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuário não está associado a uma organização",
        )

    headers = get_forwarded_headers(request)

    try:
        empresa = await auth_client.proxy_request(
            method="GET",
            path=f"/api/v1/organizations/{org_id}/companies/{empresa_id}",
            headers=headers,
        )

        return {
            "empresa_id": empresa_id,
            "ativo": empresa.get("is_active", True),
        }

    except AuthServiceError as e:
        raise HTTPException(
            status_code=e.status_code or 500,
            detail=e.message,
        )


@router.patch("/id/{empresa_id}/toggle-ativo")
async def toggle_empresa_status(
    request: Request,
    empresa_id: str,
    db: Session = Depends(get_db),
    user_data: dict[str, Any] = Depends(check_auth_with_ip),
) -> Any:
    """
    Toggle the active status of a company.
    When deactivated: all certificates for this company are also deactivated.
    When activated: all certificates for this company are also activated.
    """
    if not user_data.get("is_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas administradores podem alterar status de empresas",
        )

    org_id = user_data.get("organization_id")
    if not org_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuário não está associado a uma organização",
        )

    headers = get_forwarded_headers(request)

    try:
        # Get current status from Auth service
        empresa = await auth_client.proxy_request(
            method="GET",
            path=f"/api/v1/organizations/{org_id}/companies/{empresa_id}",
            headers=headers,
        )

        current_status = empresa.get("is_active", True)
        new_status = not current_status

        # Update status in Auth service
        await auth_client.proxy_request(
            method="PUT",
            path=f"/api/v1/organizations/{org_id}/companies/{empresa_id}",
            headers=headers,
            json={"is_active": new_status},
        )

        # Update all certificates for this empresa in local database
        cert_count = (
            db.query(Certificados)
            .filter(
                Certificados.empresa_id == empresa_id,
                Certificados.deleted_at.is_(None),
            )
            .update({"ativo": new_status})
        )

        db.commit()

        return {
            "empresa_id": empresa_id,
            "ativo": new_status,
            "certificados_atualizados": cert_count,
            "message": f"Empresa {'ativada' if new_status else 'desativada'} com sucesso. {cert_count} certificado(s) {'ativado(s)' if new_status else 'desativado(s)'}.",
        }

    except AuthServiceError as e:
        raise HTTPException(
            status_code=e.status_code or 500,
            detail=e.message,
        )