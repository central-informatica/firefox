from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.db.models import Usuarios, AccessTokens
from backend.app.schemas.auth import LoginJSON, UserCreate, UserOut
from backend.app.schemas.token import TokenContext
from backend.app.core.security import hash_password, verify_password
from backend.app.core.token_security import (
    generate_opaque_token,
    hash_validator,
    build_permissions,
    calculate_token_expiration,
)
from backend.app.core.csrf import create_csrf_token
from backend.app.core.validar_token import validar_token, validar_token_universal

router = APIRouter(prefix="/auth", tags=["Auth"])

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


@router.post("/login-web", response_model=UserOut)
async def auth_login_web(
    payload: LoginJSON,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Authenticate web application users.
    Returns session token in HTTP-only cookie + CSRF token in readable cookie.
    """
    user = (
        db.query(Usuarios)
        .filter(Usuarios.email == payload.email)
        .first()
    )

    if not user or not verify_password(payload.senha, user.senha_hash):
        raise HTTPException(403, "As credenciais não conferem")

    full_token, selector, validator = generate_opaque_token()

    permissions = build_permissions(db, user.usuario_id)

    access_token = AccessTokens(
        usuario_id=user.usuario_id,
        selector=selector,
        validator_hash=hash_validator(validator),
        tipo_cliente="WEB",
        expires_at=calculate_token_expiration(minutes=15),
        permissions=permissions,
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host if request.client else None,
    )
    db.add(access_token)
    db.commit()

    csrf = create_csrf_token()

    response = JSONResponse(
        {
            "id": user.usuario_id,
            "nome": user.nome,
            "email": user.email,
            "empresa_id": 0,
        }
    )

    response.set_cookie(
        key="session_token",
        value=full_token,
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


@router.post("/login-desktop", response_model=dict)
async def auth_login_desktop(
    payload: LoginJSON,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Authenticate desktop application users.
    Returns access token in response body (to be sent in Authorization header).
    Does not use cookies or CSRF tokens.
    """
    user = (
        db.query(Usuarios)
        .filter(Usuarios.email == payload.email)
        .first()
    )

    if not user or not verify_password(payload.senha, user.senha_hash):
        raise HTTPException(403, "As credenciais não conferem")

    # Generate opaque token (selector.validator)
    full_token, selector, validator = generate_opaque_token()

    # Build permissions cache
    permissions = build_permissions(db, user.usuario_id)

    # Create access token record for DESKTOP client
    access_token = AccessTokens(
        usuario_id=user.usuario_id,
        selector=selector,
        validator_hash=hash_validator(validator),
        tipo_cliente="DESKTOP",  # Desktop client type
        expires_at=calculate_token_expiration(minutes=15),
        permissions=permissions,
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host if request.client else None,
    )
    db.add(access_token)
    db.commit()

    # Return token in response body for desktop apps
    return {
        "access_token": full_token,
        "token_type": "Bearer",
        "expires_in": 900,  # 15 minutes in seconds
        "user": {
            "id": user.usuario_id,
            "nome": user.nome,
            "email": user.email,
        }
    }


@router.get("/me", response_model=UserOut)
async def auth_me(
    token_context: TokenContext = Depends(validar_token_universal),
    db: Session = Depends(get_db)
):
    """
    Get current authenticated user information.

    Works for both WEB and DESKTOP clients:
    - WEB: Send session cookie + X-CSRF-Token header
    - DESKTOP: Send Authorization: Bearer <token> header
    """
    usuario = (
        db.query(Usuarios)
        .filter(Usuarios.usuario_id == token_context.usuario_id)
        .first()
    )

    if not usuario:
        raise HTTPException(401, "Usuário não encontrado")

    return {
        "id": usuario.usuario_id,
        "nome": usuario.nome,
        "email": usuario.email,
        "empresa_id": 0,
    }

@router.post("/logout")
async def auth_logout(
    token_context: TokenContext = Depends(validar_token_universal),
    db: Session = Depends(get_db)
):
    """
    Logout and revoke the current token.

    Works for both WEB and DESKTOP clients:
    - WEB: Revokes token and deletes cookies
    - DESKTOP: Revokes token (client should discard the token)
    """
    # Revoke the current token
    token_record = (
        db.query(AccessTokens)
        .filter(AccessTokens.token_id == token_context.token_id)
        .first()
    )

    if token_record:
        token_record.revogado = True
        token_record.revogado_em = calculate_token_expiration(minutes=0)  # now
        token_record.revogado_motivo = "logout"
        db.commit()

    response = JSONResponse({"detail": "Logout realizado com sucesso."})

    # Delete cookies only for WEB clients
    if token_context.is_web_client():
        response.delete_cookie("session_token", path="/")
        response.delete_cookie("csrf_token", path="/")

    return response
