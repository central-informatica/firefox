import secrets
from fastapi import HTTPException, Header, Request, Depends
from backend.app.utils.db_sqlite import getDb


# ---- CSRF simples

def create_csrf_token() -> str:
    return secrets.token_urlsafe(32)

# ---- Validação de sessão (usa cookie "session_token")

def validar_token(
    request: Request,
    authorization: str | None = Header(default=None),
):
    """
    Valida o acesso pelo cookie 'session_token' ou pelo header Authorization: Bearer.
    Retorna o registro da tabela 'acesso'.
    """

    token = None

    # 1) Authorization: Bearer <token>
    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:]

    # 2) Cookie session_token
    if not token:
        token = request.cookies.get("session_token")

    if not token:
        raise HTTPException(status_code=401, detail="Token não informado")

    conexao = getDb()
    cursor = conexao.cursor()
    cursor.execute(
        "SELECT * FROM acesso WHERE token = ? AND ativo = 1",
        (token,),
    )
    acesso = cursor.fetchone()
    conexao.close()

    if not acesso:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")

    return acesso  # (id_acesso, id_usuario, token, ativo)
