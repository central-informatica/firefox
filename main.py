from fastapi import FastAPI, UploadFile, Form, HTTPException, Header, Depends, Response, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import secrets
import os
import json
import time
import traceback
import base64
from fastapi.responses import JSONResponse

from dotenv import load_dotenv
from db_sqlite import getDb
from chave_mestra import gerar_chave
from crypto_utils import encrypt_pfx, decrypt_pfx
from gerar_token_acesso import gerar_token

load_dotenv()

app = FastAPI()

# CORS para permitir o frontend (127.0.0.1:5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ================================
#  Modelos e Helpers
# ================================

class LoginJSON(BaseModel):
    email: str
    senha: str


class SignRequest(BaseModel):
    cert_id: str
    hash: str
    content: str


def create_csrf_token() -> str:
    return secrets.token_urlsafe(32)


# ================================
#  Middleware de segurança (opcional)
# ================================

@app.middleware("http")
async def add_security_headers(request, call_next):
    try:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response
    except Exception as e:
        print("Erro no middleware:", e)
        raise


# ================================
#  Token Validator (cookie + bearer)
# ================================

def validar_token(
    request: Request,
    authorization: str | None = Header(default=None)
):
    """
    Valida o token vindo do Authorization: Bearer
    OU vindo do cookie 'session_token'.
    """

    token = None

    # via header Authorization
    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:]

    # via cookie HttpOnly
    if not token:
        token = request.cookies.get("session_token")

    if not token:
        raise HTTPException(status_code=401, detail="Token não informado")

    conexao = getDb()
    cursor = conexao.cursor()
    cursor.execute("select * from acesso where token = ? and ativo = 1", (token,))
    acesso = cursor.fetchone()
    conexao.close()

    if not acesso:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")

    return acesso  # (id, id_usuario, token, ativo)


# ================================
#  ROTA /auth/login  (NOVA)
# ================================

@app.post("/auth/login")
async def auth_login(payload: LoginJSON):
    nome = payload.email
    senha = payload.senha

    conexao = getDb()
    cursor = conexao.cursor()
    cursor.execute("select * from usuarios where nome = ? and senha = ?", (nome, senha))
    usuario = cursor.fetchone()

    if not usuario:
        conexao.close()
        raise HTTPException(status_code=403, detail="As credenciais não conferem")

    token_gerado = gerar_token()
    cursor.execute(
        "insert into acesso(id_usuario, token, ativo) values (?, ?, 1)",
        (usuario[0], token_gerado)
    )
    conexao.commit()
    conexao.close()

    # cria resposta JSON
    response = JSONResponse({
        "id": usuario[0],
        "nome": usuario[1],
        "email": usuario[1],
        "empresa_id": 1
    })

    # cookie de sessão
    response.set_cookie(
        key="session_token",
        value=token_gerado,
        httponly=True,
        secure=False,     # True em produção
        samesite="Lax",
        path="/"
    )

    # cookie CSRF
    csrf = create_csrf_token()
    response.set_cookie(
        key="csrf_token",
        value=csrf,
        httponly=False,
        secure=False,
        samesite="Lax",
        path="/"
    )

    return response


# ================================
#  ROTA /auth/me  (NOVA)
# ================================

@app.get("/auth/me")
async def auth_me(acesso=Depends(validar_token)):
    """
    Retorna dados do usuário logado
    """

    id_usuario = acesso[1]

    conexao = getDb()
    cursor = conexao.cursor()
    cursor.execute("select * from usuarios where id = ?", (id_usuario,))
    usuario = cursor.fetchone()
    conexao.close()

    if not usuario:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")

    return {
        "id": usuario[0],
        "nome": usuario[1],
        "email": usuario[1],
        "empresa_id": 1,
    }


# ================================
#  ROTA /auth/logout  (NOVA)
# ================================

@app.post("/auth/logout")
async def auth_logout(response: Response, acesso=Depends(validar_token)):
    id_acesso = acesso[0]

    conexao = getDb()
    cursor = conexao.cursor()
    cursor.execute("update acesso set ativo = 0 where id = ?", (id_acesso,))
    conexao.commit()
    conexao.close()

    response.delete_cookie("session_token", path="/")
    response.delete_cookie("csrf_token", path="/")

    return {"status": "ok", "message": "logout efetuado"}


# ================================
#  ROTA /auth/refresh  (NOVA)
# ================================

@app.post("/auth/refresh")
async def auth_refresh(request: Request):
    session = request.cookies.get("session_token")
    if not session:
        raise HTTPException(401, "Sessão expirada")

    response = JSONResponse({"status": "ok"})
    response.set_cookie(
        "csrf_token",
        create_csrf_token(),
        httponly=False,
        secure=False,
        samesite="Lax",
        path="/",
    )
    return response

# ================================
#  ROTA ORIGINAL: /cadastro/usuario
# ================================

@app.post("/cadastro/usuario")
async def criar_usuario(nome: str = Form(...), senha: str = Form(...)):
    conexao = getDb()
    cursor = conexao.cursor()
    cursor.execute(
        "insert into usuarios(nome, senha) values (?, ?)",
        (nome, senha)
    )
    conexao.commit()
    conexao.close()

    return {"status": "ok", "message": "Usuário criado com sucesso"}


# ================================
#  ROTA ORIGINAL: /login (LEGADO)
# ================================
# Mantida para compatibilidade com sua versão antiga
@app.post("/login")
async def login(nome: str = Form(...), senha: str = Form(...)):
    conexao = getDb()
    cursor = conexao.cursor()
    cursor.execute("select * from usuarios where nome = ? and senha = ?", (nome, senha))
    usuario = cursor.fetchone()

    if not usuario:
        conexao.close()
        raise HTTPException(status_code=403, detail="As credenciais não conferem")

    token = gerar_token()

    cursor.execute(
        "insert into acesso(id_usuario, token, ativo) values (?, ?, 1)",
        (usuario[0], token)
    )
    conexao.commit()
    conexao.close()

    return {"status": "ok", "token": token}


# ================================
#  ROTA ORIGINAL + AJUSTADA: UPLOAD DE CERTIFICADO
# ================================

@app.post("/upload/certificado")
async def upload_certificado(
    arquivo: UploadFile,
    senha: str = Form(...),
    acesso=Depends(validar_token)
):
    print(f"token: {acesso[1]}")

    try:
        pfx_content = await arquivo.read()

        encrypted_data, b64_key = encrypt_pfx(pfx_content, senha)
        senha_encrypted = str(b64_key)
        cert_id = str(json.loads(decrypt_pfx(encrypted_data, senha))[0])

        conexao = getDb()
        cursor = conexao.cursor()
        cursor.execute(
            "INSERT INTO certificados(id_usuario, nome_arquivo, cert_id, encrypted, secret) "
            "VALUES (?, ?, ?, ?, ?)",
            (acesso[1], arquivo.filename, cert_id, f"{encrypted_data}", f"{senha_encrypted}")
        )
        conexao.commit()
        conexao.close()

        return {"status": "ok", "detail": "Certificado salvo com sucesso!"}

    except Exception as e:
        print("Erro ao enviar certificado:", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
