from datetime import datetime
from fastapi import Header, HTTPException, Depends, Request
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.db.models import AccessTokens
from backend.app.core.csrf import validate_csrf_token
from backend.app.core.token_security import verify_validator
from backend.app.schemas.token import TokenContext


def _validate_opaque_token(
    token: str,
    db: Session,
    expected_client_type: str | None = None
) -> TokenContext:
    """
    Internal function to validate opaque token (selector.validator format).

    Args:
        token: Full opaque token (selector.validator)
        db: Database session
        expected_client_type: Optional client type to verify (WEB or DESKTOP)

    Returns:
        TokenContext with user info and permissions
    """
    # Parse opaque token: selector.validator
    token_parts = token.split(".")
    if len(token_parts) != 2:
        raise HTTPException(401, "Formato de token inválido")

    selector, validator = token_parts

    # Fast lookup by selector (indexed column)
    token_record = (
        db.query(AccessTokens)
        .filter(AccessTokens.selector == selector)
        .first()
    )

    if not token_record:
        raise HTTPException(401, "Token inválido ou expirado")

    # Check if token is revoked
    if token_record.revogado:
        raise HTTPException(401, f"Token revogado: {token_record.revogado_motivo or 'sem motivo'}")

    # Check expiration
    if token_record.expires_at < datetime.utcnow():
        # Auto-revoke expired token
        token_record.revogado = True
        token_record.revogado_em = datetime.utcnow()
        token_record.revogado_motivo = "expirado"
        db.commit()
        raise HTTPException(401, "Token expirado")

    # Verify client type if specified
    if expected_client_type and token_record.tipo_cliente != expected_client_type:
        raise HTTPException(401, f"Tipo de cliente inválido. Esperado: {expected_client_type}")

    # Verify validator using Argon2
    if not verify_validator(token_record.validator_hash, validator):
        raise HTTPException(401, "Token inválido")

    # Update last use timestamp
    token_record.ultimo_uso = datetime.utcnow()
    db.commit()

    # Return TokenContext with embedded permissions
    return TokenContext(
        token_id=token_record.token_id,
        usuario_id=token_record.usuario_id,
        permissions=token_record.permissions,
        tipo_cliente=token_record.tipo_cliente
    )


async def validar_token(
    request: Request,
    csrf_token: str | None = Header(default=None, alias="X-CSRF-Token"),
    db: Session = Depends(get_db)
) -> TokenContext:
    """
    Validates WEB client session via cookies + CSRF header.

    For web applications only. Desktop apps should use validar_token_desktop.

    Returns TokenContext with user ID, permissions, and client type.

    Opaque token format: {selector}.{validator}
    - Selector: Fast indexed lookup (first 32 bytes, base64url)
    - Validator: Verified against Argon2 hash (last 32 bytes)
    """

    # Get session token from cookie
    session_token = request.cookies.get("session_token")
    if not session_token:
        raise HTTPException(401, "Token de sessão ausente")

    # Validate CSRF for WEB clients
    cookie_csrf = request.cookies.get("csrf_token")
    if not cookie_csrf:
        raise HTTPException(403, "CSRF ausente")

    if not csrf_token:
        raise HTTPException(403, "Header X-CSRF-Token ausente")

    if not validate_csrf_token(csrf_token, cookie_csrf):
        raise HTTPException(403, "CSRF inválido")

    # Validate the opaque token (WEB client type)
    return _validate_opaque_token(session_token, db, expected_client_type="WEB")


async def validar_token_desktop(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db)
) -> TokenContext:
    """
    Validates DESKTOP client session via Authorization header (Bearer token).

    For desktop applications only. Web apps should use validar_token.
    Does not require CSRF validation.

    Returns TokenContext with user ID, permissions, and client type.

    Opaque token format: {selector}.{validator}
    - Selector: Fast indexed lookup (first 32 bytes, base64url)
    - Validator: Verified against Argon2 hash (last 32 bytes)
    """

    # Get Bearer token from Authorization header
    if not authorization:
        raise HTTPException(401, "Authorization header ausente")

    # Parse Bearer token
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(401, "Formato de Authorization inválido. Use: Bearer <token>")

    bearer_token = parts[1]

    # Validate the opaque token (DESKTOP client type)
    return _validate_opaque_token(bearer_token, db, expected_client_type="DESKTOP")


async def validar_token_universal(
    request: Request,
    authorization: str | None = Header(default=None),
    csrf_token: str | None = Header(default=None, alias="X-CSRF-Token"),
    db: Session = Depends(get_db)
) -> TokenContext:
    """
    Universal token validator that supports both WEB and DESKTOP clients.

    Automatically detects client type:
    - If Authorization header present: validates as DESKTOP client (Bearer token)
    - If session_token cookie present: validates as WEB client (cookie + CSRF)

    Returns TokenContext with user ID, permissions, and client type.
    """

    # Try Desktop authentication first (Authorization header)
    if authorization:
        parts = authorization.split()
        if len(parts) == 2 and parts[0].lower() == "bearer":
            bearer_token = parts[1]
            return _validate_opaque_token(bearer_token, db, expected_client_type="DESKTOP")

    # Try Web authentication (cookie + CSRF)
    session_token = request.cookies.get("session_token")
    if session_token:
        # Validate CSRF for WEB clients
        cookie_csrf = request.cookies.get("csrf_token")
        if not cookie_csrf:
            raise HTTPException(403, "CSRF ausente")

        if not csrf_token:
            raise HTTPException(403, "Header X-CSRF-Token ausente")

        if not validate_csrf_token(csrf_token, cookie_csrf):
            raise HTTPException(403, "CSRF inválido")

        return _validate_opaque_token(session_token, db, expected_client_type="WEB")

    # No valid authentication method found
    raise HTTPException(
        401,
        "Autenticação necessária. Envie Authorization header (desktop) ou session cookie (web)"
    )
