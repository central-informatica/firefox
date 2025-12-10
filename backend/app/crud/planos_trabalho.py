from sqlalchemy.orm import Session
from backend.app.db.models import PlanosTrabalho


def listar_planos_trabalho(db: Session):
    return db.query(PlanosTrabalho).all()


def get_planos_trabalho(db: Session, plano_id: int):
    return db.query(PlanosTrabalho).filter(PlanosTrabalho.plano_id == plano_id).first()


def criar_planos_trabalho(db: Session, payload: dict):
    novo = PlanosTrabalho(**payload)
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo


def atualizar_planos_trabalho(db: Session, plano_id: int, dados: dict):
    planos_trabalho = get_planos_trabalho(db, plano_id)
    if not planos_trabalho:
        return None

    for key, value in dados.items():
        setattr(planos_trabalho, key, value)

    db.commit()
    db.refresh(planos_trabalho)
    return planos_trabalho


def deletar_planos_trabalho(db: Session, plano_id: int):
    planos_trabalho = get_planos_trabalho(db, plano_id)
    if not planos_trabalho:
        return False

    db.delete(planos_trabalho)
    db.commit()
    return True
