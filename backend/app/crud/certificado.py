from sqlalchemy.orm import Session
from backend.app.db.models import Certificados
from backend.app.schemas.certificados import CertificadoCreate

def create_certificado(db: Session, data: CertificadoCreate, file_name: str, user_id: int, user_name: str):
    novo = Certificados(
        empresa_id=data.empresa_id,
        nome_arquivo=file_name,
        senha=data.senha,
        proprietario=data.proprietario,
        emitido_por=data.emitido_por,
        validade_inicio=data.validade_inicio,
        valido_ate=data.valido_ate,
        criado_por=user_id,
        criado_por_nome=user_name,
    )
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo

def get_certificado(db: Session, certificado_id: int):
    return db.query(Certificados).filter(Certificados.id == certificado_id).first()

def delete_certificado(db: Session, certificado_id: int):
    cert = get_certificado(db, certificado_id)
    if not cert:
        return False
    db.delete(cert)
    db.commit()
    return True

def listar_certificados(db: Session, empresa_id: int, page: int, limit: int, search: str, sort: str):
    query = db.query(Certificados).filter(Certificados.empresa_id == empresa_id)

    if search:
        termo = f"%{search.lower()}%"
        query = query.filter(Certificados.nome_arquivo.ilike(termo))

    if sort:
        campo, ordem = sort.split(".")
        col = getattr(Certificados, campo)
        if ordem == "desc":
            col = col.desc()
        query = query.order_by(col)

    total = query.count()
    dados = query.offset((page - 1) * limit).limit(limit).all()

    return dados, total
