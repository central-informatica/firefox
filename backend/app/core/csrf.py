import secrets
from fastapi import Header, HTTPException, Request, status


# =========================================================
# CSRF TOKEN
# =========================================================

def gerar_csrf_token() -> str:
    return secrets.token_hex(32)


def validate_csrf_token(header_token: str, cookie_token: str) -> bool:
    return secrets.compare_digest(header_token, cookie_token)


def validar_csrf(
    request: Request,
    csrf_token: str = Header(..., alias="X-CSRF-Token"),
):
    cookie_csrf = request.cookies.get("csrf_token")

    if not cookie_csrf:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF ausente",
        )

    if not validate_csrf_token(csrf_token, cookie_csrf):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF inválido",
        )
