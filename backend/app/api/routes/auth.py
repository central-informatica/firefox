from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from backend.app.db.deps import get_db
from backend.app.db.models import Usuarios, Acesso
from backend.app.schemas.auth import LoginJSON, UserCreate, UserOut
from backend.app.core.security import (
    hash_password,
    verify_password,
    gerar_token,
)
from backend.app.core.csrf import create_csrf_token
from backend.app.core.validar_token import validar_token

router = APIRouter(prefix="/auth", tags=["Auth"])


# ----------------------------------------------------------
# REGISTER
# ----------------------------------------------------------
@router.post("/register", response_model=UserOut)
async def register_user(payload: UserCreate, db: Session = Depends(get_db)):
    existente = (
        db.query(Usuarios)
        .filter(Usuarios.email == payload.email)
        .first()
    )

    if existente:
        raise HTTPException(400, "Email já está cadastrado.")

    senha_hash = hash_password(payload.senha)

    novo = Usuarios(
        nome=payload.nome,
        email=payload.email,
        telefone=payload.telefone,
        senha_hash=senha_hash,
    )

    db.add(novo)
    db.commit()
    db.refresh(novo)

    return {
        "id": novo.usuario_id,
        "nome": novo.nome,
        "email": novo.email,
    }


@router.post("/login", response_model=UserOut)
async def auth_login(payload: LoginJSON, db: Session = Depends(get_db)):
    user = (
        db.query(Usuarios)
        .filter(Usuarios.email == payload.email)
        .first()
    )

    if not user or not verify_password(payload.senha, user.senha_hash):
        raise HTTPException(403, "As credenciais não conferem")

    token = gerar_token()

    acesso = Acesso(id_usuario=user.usuario_id, token=token, ativo=True)
    db.add(acesso)
    db.commit()

    csrf = create_csrf_token()

    response = JSONResponse(
        {
            "id": user.usuario_id,
            "nome": user.nome,
            "email": user.email,
            "empresa_id": user.empresa_id,
        }
    )

    response.set_cookie(
        key="session_token",
        value=token,
        httponly=True,
        secure=False,
        samesite="lax",
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


# ----------------------------------------------------------
# ME
# ----------------------------------------------------------
@router.get("/me", response_model=UserOut)
async def auth_me(acesso=Depends(validar_token), db: Session = Depends(get_db)):
    usuario = (
        db.query(Usuarios)
        .filter(Usuarios.usuario_id == acesso.id_usuario)
        .first()
    )

    if not usuario:
        raise HTTPException(401, "Usuário não encontrado")

    return {
        "id": usuario.usuario_id,
        "nome": usuario.nome,
        "email": usuario.email,
        "empresa_id": usuario.empresa_id,
    }


# ----------------------------------------------------------
# LOGOUT
# ----------------------------------------------------------
@router.post("/logout")
async def auth_logout(acesso=Depends(validar_token), db: Session = Depends(get_db)):
    acesso.ativo = False
    db.commit()

    response = JSONResponse({"detail": "Logout realizado com sucesso."})
    response.delete_cookie("session_token", path="/")
    response.delete_cookie("csrf_token", path="/")
    return response


# ----------------------------------------------------------
# REFRESH
# ----------------------------------------------------------
@router.post("/refresh", response_model=UserOut)
async def refresh_token(acesso=Depends(validar_token), db: Session = Depends(get_db)):
    acesso.ativo = False
    db.commit()

    novo_token = gerar_token()
    novo = Acesso(id_usuario=acesso.id_usuario, token=novo_token, ativo=True)
    db.add(novo)
    db.commit()

    csrf = create_csrf_token()

    usuario = (
        db.query(Usuarios)
        .filter(Usuarios.usuario_id == acesso.id_usuario)
        .first()
    )

    response = JSONResponse({
        "id": usuario.usuario_id,
        "nome": usuario.nome,
        "email": usuario.email,
        "empresa_id": usuario.empresa_id,
    })

    response.set_cookie(
        key="session_token",
        value=novo_token,
        httponly=True,
        secure=False,
        samesite="lax",
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
