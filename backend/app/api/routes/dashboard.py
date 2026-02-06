"""
Dashboard routes - statistics and metrics.
"""

from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from backend.app.api.deps import check_auth_with_ip
from backend.app.db.models import Certificados
from backend.app.db.session import get_db
from backend.app.services.auth_client import auth_client, AuthServiceError

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats")
async def get_dashboard_stats(
    request: Request,
    user_data: dict[str, Any] = Depends(check_auth_with_ip),
    db: Session = Depends(get_db),
) -> Any:
    """
    Get dashboard statistics.

    Returns:
    - total_usuarios: Total number of users in the organization
    - certificados_ativos: Total number of active certificates across all companies
    """
    try:
        # Get organization_id from authenticated user
        organization_id = user_data.get("organization_id")
        if not organization_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Organization ID not found in user data",
            )

        # Get total users from Auth service
        session_token = request.cookies.get("session_token")
        if not session_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session token not found",
            )

        headers = {"Authorization": f"Bearer {session_token}"}

        try:
            users_response = await auth_client.proxy_request(
                method="GET",
                path=f"/api/v1/users/?limit=100",  # Max limit is 100
                headers=headers,
            )

            print(f"DEBUG: users_response type: {type(users_response)}")
            print(f"DEBUG: users_response content: {users_response}")

            # Extract user count
            total_usuarios = 0
            if isinstance(users_response, dict):
                total_usuarios = users_response.get("total", 0)
                print(f"DEBUG: Extracted total from dict: {total_usuarios}")
            elif isinstance(users_response, list):
                total_usuarios = len(users_response)
                print(f"DEBUG: Counted list length: {total_usuarios}")
            else:
                print(f"DEBUG: Unexpected response type: {type(users_response)}")

        except AuthServiceError as e:
            # If auth service fails, return 0 for users
            print(f"Error fetching users from auth service: {e}")
            total_usuarios = 0

        # Get active certificates count from database
        # Count certificates where ativo=true (not considering empresa_id since we want organization-wide)
        stmt = select(func.count(Certificados.certificado_id)).where(
            Certificados.ativo == True  # noqa: E712
        )
        result = db.execute(stmt)
        certificados_ativos = result.scalar() or 0

        return {
            "total_usuarios": total_usuarios,
            "certificados_ativos": certificados_ativos,
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_dashboard_stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching dashboard stats: {str(e)}",
        )
