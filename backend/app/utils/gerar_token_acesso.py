import secrets

def gerar_token():
    return secrets.token_urlsafe(32)  # gera string segura de 32 bytes (~43 chars)
