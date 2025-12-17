from backend.app.db.models import Empresas
from tests.factories.base import commit_and_refresh

def criar_empresa(db, usuario_id):
    empresa = Empresas(
        razao_social="Empresa Teste LTDA",
        fantasia="Empresa Teste",
        cnpj="12345678000199",
        anfitria_usuario_id=usuario_id,
        timezone="America/Sao_Paulo",
    )
    return commit_and_refresh(db, empresa)