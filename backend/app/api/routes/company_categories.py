"""
Company categories routes - proxies to Auth microservice.

Provides list of company activity sectors/categories from the Auth service.
"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request

from backend.app.api.deps import check_auth_with_ip
from backend.app.core.exceptions import AuthServiceError
from backend.app.services.auth_client import auth_client

router = APIRouter(prefix="/company-categories", tags=["Company Categories"])

# Headers to exclude when forwarding
EXCLUDED_HEADERS = {'content-length', 'host', 'transfer-encoding', 'content-type'}


def get_forwarded_headers(request: Request) -> dict[str, str]:
    """Extract headers to forward, excluding hop-by-hop and body-related headers."""
    return {
        k: v for k, v in request.headers.items()
        if k.lower() not in EXCLUDED_HEADERS
    }


@router.get("/")
async def list_company_categories(
    request: Request,
    user_data: dict[str, Any] = Depends(check_auth_with_ip),
) -> Any:
    """
    List all company categories (activity sectors).

    Forwards request to Auth service /api/v1/company-categories.
    Returns list of categories for select dropdowns.
    """
    headers = get_forwarded_headers(request)

    try:
        return await auth_client.proxy_request(
            method="GET",
            path="/api/v1/company-categories",
            headers=headers,
        )

    except AuthServiceError as e:
        raise HTTPException(
            status_code=e.status_code or 500,
            detail=e.message,
        )
