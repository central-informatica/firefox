from backend.app.db.models import Certificados
from tests.factories.base import commit_and_refresh

def criar_certificado(
    db,
    empresa_id,
    criado_por=None,
    nome_arquivo="teste.pfx",
    encrypted="encrypted-data",
    secret="secret",
    ativo=True,
):
    cert = Certificados(
        empresa_id=empresa_id,
        criado_por=criado_por,
        nome_arquivo=nome_arquivo,
        encrypted=encrypted,
        secret=secret,
        ativo=ativo,
    )
    return commit_and_refresh(db, cert)
