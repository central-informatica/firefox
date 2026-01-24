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

from backend.app.core.exceptions import AuthServiceError
from backend.app.services.auth_client import auth_client

# Headers to exclude when forwarding
EXCLUDED_HEADERS = {'content-length', 'host', 'transfer-encoding', 'content-type'}


async def check_auth(request: Request) -> dict[str, Any]:
    """
    Check if user is authenticated by forwarding to Auth service /api/v1/auth/me.

    Returns:
        dict with user information from Auth service

    Raises:
        HTTPException 401: If not authenticated
    """
    headers = {
        k: v for k, v in request.headers.items()
        if k.lower() not in EXCLUDED_HEADERS
    }

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


