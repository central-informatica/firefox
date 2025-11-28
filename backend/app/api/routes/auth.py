from fastapi import APIRouter, HTTPException, Response, Depends
from fastapi import Request
from fastapi.responses import JSONResponse

from sqlalchemy.orm import Session

from backend.app.schemas.auth import LoginJSON, UserOut
from backend.app.core.security import create_csrf_token, validar_token
from backend.app.utils.gerar_token_acesso import gerar_token
#from backend.app.utils.db_sqlite import getDb

from backend.app.db.deps import get_db
from backend.app.db.models import Usuarios, Acesso
from backend.app.schemas.auth import UserCreate

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=UserOut)
async def auth_login(payload: LoginJSON, db: Session = Depends(get_db)):
    """
    Login via JSON (email + senha) usando SQLAlchemy.
    Cria cookie de sessão + cookie CSRF.
    """

    # Buscar usuário no banco
    user = (
        db.query(Usuarios)
        .filter(
            Usuarios.email == payload.email,
            Usuarios.senha_hash == hash_password(payload.senha),
        )
        .first()
    )

    if not user:
        raise HTTPException(403, "As credenciais não conferem")

    # Gerar token de sessão
    token = gerar_token()

    acesso = Acesso(
        id_usuario=user.usuario_id,
        token=token,
        ativo=True
    )
    db.add(acesso)
    db.commit()

    # Criar CSRF
    csrf = create_csrf_token()

    # Resposta com dados do usuário
    response = JSONResponse(
        {
            "id": user.usuario_id,
            "nome": user.nome,
            "email": user.email,
            "empresa_id": user.empresa_id,
        }
    )

    # Definir cookies corretamente
    response.set_cookie(
        key="session_token",
        value=token,
        httponly=True,
        secure=False,  # PRODUÇÃO = True
        samesite="lax",  # PRODUÇÃO = "none"
        path="/",
    )

    response.set_cookie(
        key="csrf_token",
        value=csrf,
        httponly=False,  # JS precisa ler
        secure=False,  # PRODUÇÃO = True
        samesite="lax",  # PRODUÇÃO = "none"
        path="/",
    )

    return response


@router.get("/me", response_model=UserOut)
async def auth_me(acesso = Depends(validar_token), db: Session = Depends(get_db)):
    """
    Retorna o usuário logado com base no token de sessão.
    """
    id_usuario = acesso.id_usuario

    usuario = (
        db.query(Usuarios)
        .filter(Usuarios.usuario_id == id_usuario)
        .first()
    )

    if not usuario:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")

    return {
        "id": usuario.usuario_id,
        "nome": usuario.nome,
        "email": usuario.email,
    }
        #"empresa_id": usuario.empresa_id,

@router.post("/logout")
async def auth_logout(
    acesso = Depends(validar_token),
    db: Session = Depends(get_db)
):
    """
    Invalida o token de sessão e remove cookies.
    """

    # Desativar o token de sessão no banco
    acesso.ativo = False
    db.commit()

    # Criar resposta vazia
    response = JSONResponse({"detail": "Logout realizado com sucesso."})

    # Remover session_token
    response.delete_cookie(
        key="session_token",
        path="/"
    )

    # 4️⃣ Remover csrf_token
    response.delete_cookie(
        key="csrf_token",
        path="/"
    )

    return response


@router.post("/refresh", response_model=UserOut)
async def refresh_token(
    acesso = Depends(validar_token),
    db: Session = Depends(get_db)
):
    """
    Renova o token de sessão do usuário.
    Gera novo session_token + novo csrf_token.
    """

    # 1️⃣ Desativa token atual
    acesso.ativo = False
    db.commit()

    # 2️⃣ Gerar novo token de sessão
    novo_token = gerar_token()

    novo_acesso = Acesso(
        id_usuario=acesso.id_usuario,
        token=novo_token,
        ativo=True
    )
    db.add(novo_acesso)
    db.commit()

    # 3️⃣ Criar novo csrf
    csrf = create_csrf_token()

    # 4️⃣ Obter usuário logado
    usuario = (
        db.query(Usuarios)
        .filter(Usuarios.usuario_id == acesso.id_usuario)
        .first()
    )

    # 5️⃣ Resposta final
    response = JSONResponse({
        "id": usuario.usuario_id,
        "nome": usuario.nome,
        "email": usuario.email,
        "empresa_id": usuario.empresa_id,
    })

    # 6️⃣ Definir novos cookies
    response.set_cookie(
        key="session_token",
        value=novo_token,
        httponly=True,
        secure=False,     # produção = True
        samesite="lax",   # produção = none
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


@router.post("/register", response_model=UserOut)
async def register_user(
    payload: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Registra um novo usuário usando SQLAlchemy e bcrypt.
    """

    # Verificar se já existe usuário com email
    existente = (
        db.query(Usuarios)
        .filter(Usuarios.email == payload.email)
        .first()
    )

    if existente:
        raise HTTPException(400, "Email já está cadastrado.")

    # Criar hash da senha
    senha_hash = hash_password(payload.senha)

    # Criar objeto usuario
    novo = Usuarios(
        nome=payload.nome,
        email=payload.email,
        senha_hash=senha_hash,
        empresa_id=None  # se quiser vincular depois
    )

    db.add(novo)
    db.commit()
    db.refresh(novo)

    # Retorno padronizado
    return {
        "id": novo.usuario_id,
        "nome": novo.nome,
        "email": novo.email,
        "empresa_id": novo.empresa_id,
    }

