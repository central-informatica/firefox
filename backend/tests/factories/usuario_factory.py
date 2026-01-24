from backend.app.db.models import Usuarios
from backend.app.core.security import hash_password
from tests.factories.base import commit_and_refresh

def criar_usuario(
    db,
    nome="Admin",
    email="admin@test.com",
    senha="123456",
    verificado=True,
):
    usuario = Usuarios(
        nome=nome,
        email=email,
        senha_hash=hash_password(senha),
        email_verificado=verificado,
    )
    return commit_and_refresh(db, usuario)
