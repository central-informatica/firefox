from sqlalchemy.orm import Session
from backend.app.db.models import Usuarios, Empresas, EmpresaMembros


def get_usuario(db: Session, usuario_id: int):
    return db.query(Usuarios).filter(Usuarios.usuario_id == usuario_id).first()


def get_usuario_por_email(db: Session, email: str):
    return db.query(Usuarios).filter(Usuarios.email == email).first()


def listar_empresas_do_usuario(db: Session, usuario_id: int):
    empresas = (
        db.query(Empresas)
        .join(EmpresaMembros, EmpresaMembros.empresa_id == Empresas.empresa_id)
        .filter(EmpresaMembros.usuario_id == usuario_id)
        .all()
    )

    return empresas


def criar_usuario(db: Session, usuario: dict):
    novo = Usuarios(**usuario)
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo


def atualizar_usuario(db: Session, usuario_id: int, dados: dict):
    usuario = get_usuario(db, usuario_id)
    if not usuario:
        return None

    for key, value in dados.items():
        setattr(usuario, key, value)

    db.commit()
    db.refresh(usuario)
    return usuario


def deletar_usuario(db: Session, usuario_id: int):
    usuario = get_usuario(db, usuario_id)
    if not usuario:
        return False

    db.delete(usuario)
    db.commit()
    return True
