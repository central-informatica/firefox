from fastapi import Header, HTTPException, Depends, Request
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.db.models import Acesso
from backend.app.core.csrf import validate_csrf_token


async def validar_token(
    request: Request,
    csrf_token: str | None = Header(default=None, alias="X-CSRF-Token"),
    db: Session = Depends(get_db)
):
    """
    Valida sessão via cookies + header CSRF.
    Retorna objeto Acesso (id_usuario, token, ativo...).
    """

    session_token = request.cookies.get("session_token")
    if not session_token:
        raise HTTPException(401, "Token de sessão ausente")

    cookie_csrf = request.cookies.get("csrf_token")
    if not cookie_csrf:
        raise HTTPException(403, "CSRF ausente")

    if not csrf_token:
        raise HTTPException(403, "Header X-CSRF-Token ausente")

    if not validate_csrf_token(csrf_token, cookie_csrf):
        raise HTTPException(403, "CSRF inválido")

    acesso = (
        db.query(Acesso)
        .filter(Acesso.token == session_token, Acesso.ativo == True)
        .first()
    )

    if not acesso:
        raise HTTPException(401, "Sessão inválida ou expirada")

    return acesso
