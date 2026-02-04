"""
Dependencias da API (FastAPI Depends).

Funcoes definidas aqui sao injetadas automaticamente nos endpoints
via `Depends()`, como autenticacao do usuario, verificacao de sessao,
controle de acesso e outras validacoes compartilhadas.

Authentication is now delegated to the Auth microservice (port 8001).
User data is returned as a dict from the Auth service, not a local model.
"""

from typing import Any

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from backend.app.core.exceptions import (
    AuthServiceError,
    CircuitBreakerOpenError,
    ServiceError,
    ServiceTimeoutError,
    ServiceUnavailableError,
)
from backend.app.services.auth_client import auth_client

# Headers to exclude when forwarding
EXCLUDED_HEADERS = {'content-length', 'host', 'transfer-encoding', 'content-type'}


async def check_auth(request: Request) -> dict[str, Any]:
    """
    Check if user is authenticated by forwarding to Auth service /api/v1/auth/me.

    Reads session_token from HttpOnly cookie and converts to Authorization header.

    Returns:
        dict with user information from Auth service

    Raises:
        HTTPException 401: If not authenticated
    """
    # Get session token from cookie
    session_token = request.cookies.get("session_token")

    if not session_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
        )

    # Build headers, excluding certain ones
    headers = {
        k: v for k, v in request.headers.items()
        if k.lower() not in EXCLUDED_HEADERS
    }

    # Add Authorization header with session token from cookie
    headers["Authorization"] = f"Bearer {session_token}"

    try:
        return await auth_client.proxy_request(
            method="GET",
            path="/api/v1/auth/me",
            headers=headers,
        )
    except AuthServiceError as e:
        raise HTTPException(
            status_code=e.status_code or status.HTTP_401_UNAUTHORIZED,
            detail=e.message or "Nao autenticado",
        )
    except ServiceTimeoutError:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Servico de autenticacao demorou muito para responder",
        )
    except ServiceUnavailableError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Servico de autenticacao indisponivel",
        )
    except CircuitBreakerOpenError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Servico de autenticacao temporariamente bloqueado",
        )
    except ServiceError as e:
        raise HTTPException(
            status_code=e.status_code or status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=e.message or "Erro ao verificar autenticacao",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro inesperado ao verificar autenticacao: {str(e)}",
        )


async def check_auth_with_ip(request: Request) -> dict[str, Any]:
    """
    Check if user is authenticated and validates IP whitelist.

    Returns:
        dict with user information from Auth service

    Raises:
        HTTPException 401: If not authenticated
        HTTPException 403: If IP not whitelisted
    """
    import logging

    logger = logging.getLogger(__name__)
    user_data = await check_auth(request)

    # IP Whitelist validation
    # Auth service returns ip_address in response
    client_ip = user_data.get("ip_address")
    usuario_id = user_data.get("id") or user_data.get("usuario_id")
    empresa_id = user_data.get("organization_id")

    if empresa_id and client_ip and usuario_id:
        from backend.app.db.session import SessionLocal
        from backend.app.crud.usuarios_ip_whitelist import crud_usuarios_ip_whitelist

        db = SessionLocal()
        try:
            ip_allowed = crud_usuarios_ip_whitelist.verificar_ip_permitido(
                db, usuario_id, empresa_id, client_ip
            )
            if not ip_allowed:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Acesso negado: IP nao autorizado para este usuario/empresa, {client_ip}",
                )
        except HTTPException:
            # Re-raise HTTP exceptions (like 403 for IP not allowed)
            raise
        except Exception as e:
            # Log the error but allow access if IP whitelist check fails
            # This handles cases like missing table, database errors, etc.
            logger.warning(
                f"IP whitelist check failed (allowing access): {type(e).__name__}: {e}"
            )
        finally:
            db.close()

    return user_data


def get_user_id_from_data(user_data: dict[str, Any]) -> str:
    """
    Extrai o ID do usuario dos dados retornados pelo Auth service.

    Args:
        user_data: Dados do usuario do Auth service

    Returns:
        ID do usuario (UUID string)
    """
    # Auth service may return 'id' or 'usuario_id'
    user_id = user_data.get("id") or user_data.get("usuario_id")
    if not user_id:
        raise ValueError("User ID not found in user data")
    return user_id


def get_organization_id_from_data(user_data: dict[str, Any]) -> str | None:
    """
    Extrai o ID da organizacao dos dados retornados pelo Auth service.

    Args:
        user_data: Dados do usuario do Auth service

    Returns:
        ID da organizacao (UUID string) ou None se nao estiver em uma organizacao
    """
    org_id = user_data.get("organization_id")
    return org_id if org_id else None


def verificar_acesso_certificado(
    db: Session,
    usuario_id: str,
    certificado_id: str,
    empresa_id: str
) -> bool:
    """
    Check if a user has access to a certificate via group membership.

    Access is granted if the user belongs to a group that has access to the certificate.

    Args:
        db: Database session
        usuario_id: User ID
        certificado_id: Certificate ID
        empresa_id: Company ID

    Returns:
        True if user has access, False otherwise
    """
    from backend.app.db.models import GruposUsuarios, GruposCertificados

    # Find groups the user belongs to in this empresa
    user_groups = db.query(GruposUsuarios.grupo_id).filter(
        GruposUsuarios.usuario_id == usuario_id,
        GruposUsuarios.empresa_id == empresa_id
    ).subquery()

    # Check if any of those groups have access to the certificate
    access = db.query(GruposCertificados).filter(
        GruposCertificados.certificado_id == certificado_id,
        GruposCertificados.grupo_id.in_(user_groups)
    ).first()

    return access is not None


