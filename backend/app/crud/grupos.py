from sqlalchemy.orm import Session
from backend.app.db.models import Grupos


def listar_grupos(db: Session):
    return db.query(Grupos).all()


def get_grupo(db: Session, grupo_id: int):
    return db.query(Grupos).filter(Grupos.grupo_id == grupo_id).first()


def criar_grupo(db: Session, payload: dict):
    novo = Grupos(**payload)
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo


def atualizar_grupo(db: Session, grupo_id: int, dados: dict):
    grupo = get_grupo(db, grupo_id)
    if not grupo:
        return None

    for key, value in dados.items():
        setattr(grupo, key, value)

    db.commit()
    db.refresh(grupo)
    return grupo


def deletar_grupo(db: Session, grupo_id: int):
    grupo = get_grupo(db, grupo_id)
    if not grupo:
        return False

    db.delete(grupo)
    db.commit()
    return True
