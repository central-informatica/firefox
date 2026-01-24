"""
Permission utilities.

Note: User data is now managed by the Auth microservice.
The permission checks here work with user data from the Auth service session,
not from a local Usuarios model.
"""

from sqlalchemy import text
from sqlalchemy.orm import Session
from typing import Optional, Any
from fastapi import HTTPException


def eh_super_admin(user_data: Any) -> bool:
    """
    Check if user is a super admin.

    Args:
        user_data: User data from Auth service session (contains nivel/role info)
    """
    # Handle dict-like user data from Auth service
    if hasattr(user_data, 'nivel'):
        nivel = user_data.nivel
    elif isinstance(user_data, dict):
        nivel = user_data.get('nivel', '')
    else:
        nivel = ''

    return (nivel or "").upper() == "ADMINISTRADOR"


def usuario_pode_gerenciar(db: Session, user_data: Any, empresa_id: Optional[str]):
    """
    Check if user can manage resources for an empresa.

    Args:
        db: Database session
        user_data: User data from Auth service session
        empresa_id: The empresa ID to check permissions for
    """
    if eh_super_admin(user_data):
        return  # super admin passes without context

    if not empresa_id:
        raise HTTPException(status_code=403, detail="Identificador da empresa não foi informado!")

    # Get usuario_id from user_data
    if hasattr(user_data, 'usuario_id'):
        usuario_id = user_data.usuario_id
    elif isinstance(user_data, dict):
        usuario_id = user_data.get('usuario_id')
    else:
        raise HTTPException(status_code=403, detail="Dados de usuário inválidos")

    if not pode_gerenciar_usuarios(db=db, usuario_id=str(usuario_id), empresa_id=empresa_id):
        raise HTTPException(
            status_code=403,
            detail="Desculpe, você não tem permissão para isso!"
        )


def pode_gerenciar_usuarios(
    db: Session,
    usuario_id: str,
    empresa_id: str,
) -> bool:
    """
    Check if user can manage other users in an empresa.

    This calls a database function that checks permissions based on
    the user's role within the organization.
    """
    sql = text(
        """
        SELECT public.pode_gerenciar_usuarios(
            :usuario_id,
            :empresa_id
        )
        """
    )

    return bool(
        db.execute(
            sql,
            {
                "usuario_id": usuario_id,
                "empresa_id": empresa_id,
            },
        ).scalar()
    )
