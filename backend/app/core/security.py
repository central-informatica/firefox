from datetime import datetime
from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.db.models import Usuarios, AccessTokens
from backend.app.core.crypto import verify_argon2


def validar_token(
    request: Request,
    db: Session = Depends(get_db),
) -> Usuarios:
    """
    Valida sessão baseada em cookie httpOnly (token opaco).
    Usa padrão selector.validator com Argon2 no validator.
    Retorna o usuário autenticado.
    """

    # 1. Cookie obrigatório
    session_token = request.cookies.get("session_token")
    if not session_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sessão ausente",
        )

    # 2. Token deve estar no formato selector.validator
    try:
        selector, validator = session_token.split(".", 1)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de sessão malformado",
        )

    # 3. Buscar token pelo selector (lookup rápido, seguro)
    access_token = (
        db.query(AccessTokens)
        .filter(
            AccessTokens.selector == selector,
            AccessTokens.revogado.is_(False),
            AccessTokens.expires_at > datetime.utcnow(),
        )
        .first()
    )

    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sessão inválida ou expirada",
        )

    # 4. Verificar validator com Argon2
    if not verify_argon2(validator, access_token.validator_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sessão inválida",
        )

    # 5. Atualizar último uso (sliding session)
    access_token.ultimo_uso = datetime.utcnow()
    db.commit()

    return access_token.usuarios
