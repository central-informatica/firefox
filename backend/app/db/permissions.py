from sqlalchemy import text
from sqlalchemy.orm import Session
from typing import Optional
from fastapi import HTTPException

from backend.app.db.models import Usuarios

def eh_super_admin(usuario: Usuarios) -> bool:
    return (usuario.nivel or "").upper() == "ADMINISTRADOR"

def usuario_pode_gerenciar(db: Session, usuario_logado: Usuarios, empresa_id: Optional[int]):
    if eh_super_admin(usuario_logado):
        return  # super admin passa sem contexto

    if not empresa_id:
        raise HTTPException(status_code=403, detail="Identificador da empresa não foi informado!")

    if not pode_gerenciar_usuarios(db=db, usuario_id=usuario_logado.usuario_id, empresa_id=empresa_id):
        raise HTTPException(
            status_code=403,
            detail="Desculpe, você não tem permissão para isso!"
        )


def pode_gerenciar_usuarios(
    db: Session,
    usuario_id: int,
    empresa_id: int,
) -> bool:
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
