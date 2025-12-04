from fastapi import Header, HTTPException, Depends, Request

from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.db.models import Acesso
from backend.app.core.csrf import validate_csrf_token

import bcrypt
import secrets


async def validar_token(
    request: Request,
    csrf_token: str | None = Header(default=None, alias="X-CSRF-Token"),
    db: Session = Depends(get_db)
):
    """
    Valida:
    - cookie session_token (HttpOnly)
    - header X-CSRF-Token
    Retorna o objeto Acesso do usuário autenticado.
    """

    # Ler token de sessão do cookie
    session_token = request.cookies.get("session_token")

    if not session_token:
        raise HTTPException(401, "Token de sessão ausente")

    # Validar CSRF
    cookie_csrf = request.cookies.get("csrf_token")

    if not cookie_csrf:
        raise HTTPException(403, "CSRF ausente")

    if not csrf_token:
        raise HTTPException(403, "Header X-CSRF-Token ausente")

    if not validate_csrf_token(csrf_token, cookie_csrf):
        raise HTTPException(403, "CSRF inválido")

    # Buscar sessão no banco
    acesso = (
        db.query(Acesso)
        .filter(
            Acesso.token == session_token,
            Acesso.ativo == True
        )
        .first()
    )

    if not acesso:
        raise HTTPException(401, "Sessão inválida ou expirada")

    return acesso

def hash_password(password: str) -> str:
    """
    Gera hash seguro para senha usando bcrypt.
    """
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica se a senha informada confere com o hash armazenado.
    """
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )

def gerar_token() -> str:
    return secrets.token_hex(32)


#import secrets
#from fastapi import HTTPException, Header, Request, Depends
#from backend.app.utils.db_sqlite import getDb
# ---- CSRF simples

#def create_csrf_token() -> str:
#    return secrets.token_urlsafe(32)
#
## ---- Validação de sessão (usa cookie "session_token")
#
#def validar_token(
#    request: Request,
#    authorization: str | None = Header(default=None),
#):
#    """
#    Valida o acesso pelo cookie 'session_token' ou pelo header Authorization: Bearer.
#    Retorna o registro da tabela 'acesso'.
#    """
#
#    token = None
#
#    # 1) Authorization: Bearer <token>
#    if authorization and authorization.startswith("Bearer "):
#        token = authorization[7:]
#
#    # 2) Cookie session_token
#    if not token:
#        token = request.cookies.get("session_token")
#
#    if not token:
#        raise HTTPException(status_code=401, detail="Token não informado")
#
#    conexao = getDb()
#    cursor = conexao.cursor()
#    cursor.execute(
#        "SELECT * FROM acesso WHERE token = ? AND ativo = 1",
#        (token,),
#    )
#    acesso = cursor.fetchone()
#    conexao.close()
#
#    if not acesso:
#        raise HTTPException(status_code=401, detail="Token inválido ou expirado")
#
#    return acesso  # (id_acesso, id_usuario, token, ativo)
