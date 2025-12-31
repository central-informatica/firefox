from sqlalchemy.orm import Session
from sqlalchemy import exists, and_, or_
from fastapi import HTTPException, status

from backend.app.db.models import Empresas, EmpresaMembros  # ajuste nomes se diferente


def exigir_acesso_empresa(db: Session, empresa_id: int, usuario_id: int):
    # 1️⃣ Se for anfitrião, acesso garantido
    empresa = (
        db.query(Empresas)
        .filter(
            Empresas.empresa_id == empresa_id,
            Empresas.anfitria_usuario_id == usuario_id,
        )
        .first()
    )

    if empresa:
        return  # acesso OK

    # 2️⃣ Se for membro, acesso garantido
    membro = (
        db.query(EmpresaMembros)
        .filter(
            EmpresaMembros.empresa_id == empresa_id,
            EmpresaMembros.usuario_id == usuario_id,
        )
        .first()
    )

    if membro:
        return  # acesso OK

    # Quem não for anfitrião nem membro, sem acesso
    raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem acesso a esta empresa.",
    )
