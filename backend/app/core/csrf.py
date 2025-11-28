import secrets


def create_csrf_token() -> str:
    return secrets.token_urlsafe(32)


def validate_csrf_token(header_token: str, cookie_token: str) -> bool:
    return header_token == cookie_token
