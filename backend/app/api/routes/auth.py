from fastapi import APIRouter, HTTPException, Form, Response, Depends
from fastapi import Request
from fastapi.responses import JSONResponse

from backend.app.schemas.auth import LoginJSON, UserOut
from backend.app.core.security import create_csrf_token, validar_token
from backend.app.utils.gerar_token_acesso import gerar_token
from backend.app.utils.db_sqlite import getDb

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=UserOut)
async def auth_login(payload: LoginJSON):
    """
    Login via JSON (email + senha).
    Cria cookie de sessão (SameSite=Lax, Secure=False no DEV).
    """
    nome = payload.email
    senha = payload.senha

    conn = getDb()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM usuarios WHERE nome = ? AND senha = ?",
        (nome, senha),
    )
    usuario = cursor.fetchone()

    if not usuario:
        conn.close()
        raise HTTPException(status_code=403, detail="As credenciais não conferem")

    token_gerado = gerar_token()
    cursor.execute(
        "INSERT INTO acesso(id_usuario, token, ativo) VALUES (?, ?, 1)",
        (usuario[0], token_gerado),
    )
    conn.commit()
    conn.close()

    csrf = create_csrf_token()

    response = JSONResponse(
        {
            "id": usuario[0],
            "nome": usuario[1],
            "email": usuario[1],
            "empresa_id": 1,
        }
    )

    # cookies para AMBIENTE LOCAL
    response.set_cookie(
        key="session_token",
        value=token_gerado,
        httponly=True,
        secure=False,     # em produção: True
        samesite="lax",   # dev: LAX (funcionando), prod: 'none'
        path="/",
    )

    response.set_cookie(
        key="csrf_token",
        value=csrf,
        httponly=False,
        secure=False,
        samesite="lax",
        path="/",
    )

    return response


@router.get("/me", response_model=UserOut)
async def auth_me(acesso=Depends(validar_token)):
    """
    Retorna o usuário logado com base no token de sessão.
    """
    id_usuario = acesso[1]

    conn = getDb()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE id = ?", (id_usuario,))
    usuario = cursor.fetchone()
    conn.close()

    if not usuario:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")

    return {
        "id": usuario[0],
        "nome": usuario[1],
        "email": usuario[1],
        "empresa_id": 1,
    }


@router.post("/logout")
async def auth_logout(response: Response, acesso=Depends(validar_token)):
    """
    Invalida o token na tabela 'acesso' e apaga cookies.
    """
    id_acesso = acesso[0]

    conn = getDb()
    cursor = conn.cursor()
    cursor.execute("UPDATE acesso SET ativo = 0 WHERE id = ?", (id_acesso,))
    conn.commit()
    conn.close()

    response = JSONResponse({"status": "ok", "message": "logout efetuado"})

    response.delete_cookie("session_token", path="/")
    response.delete_cookie("csrf_token", path="/")

    return response


@router.post("/refresh")
async def auth_refresh(request: Request):
    """
    Apenas renova o csrf_token se a sessão ainda estiver ativa.
    """
    session_token = request.cookies.get("session_token")
    if not session_token:
        raise HTTPException(status_code=401, detail="Sessão expirada")

    conn = getDb()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM acesso WHERE token = ? AND ativo = 1",
        (session_token,),
    )
    acesso = cursor.fetchone()
    conn.close()

    if not acesso:
        raise HTTPException(status_code=401, detail="Sessão inválida")

    csrf = create_csrf_token()
    response = JSONResponse({"status": "ok"})

    response.set_cookie(
        key="csrf_token",
        value=csrf,
        httponly=False,
        secure=False,
        samesite="lax",
        path="/",
    )

    return response
