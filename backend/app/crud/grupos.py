from sqlalchemy.orm import Session
from fastapi import HTTPException
from backend.app.db.models import Grupos, EmpresaMembros

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


#def atualizar_grupo(db: Session, grupo_id: int, dados: dict):
#    grupo = get_grupo(db, grupo_id)
#    if not grupo:
#        return None
#
#    for key, value in dados.items():
#        setattr(grupo, key, value)
#
#    db.commit()
#    db.refresh(grupo)
#    return grupo

def atualizar_grupo(
    db: Session,
    *,
    grupo_id: int,
    empresa_id: int,
    usuario_id: int,
    dados: dict,
):
    # 1. Verifica se o usuário pertence à empresa
    if not _usuario_pertence_empresa(db, usuario_id, empresa_id):
        raise HTTPException(
            status_code=403,
            detail="Usuário não pertence à empresa",
        )

    # 2. Busca o grupo garantindo que ele pertence à empresa
    grupo = (
        db.query(Grupos)
        .filter(
            Grupos.grupo_id == grupo_id,
            Grupos.empresa_id == empresa_id,
        )
        .first()
    )

    if not grupo:
        return None

    # 3. Atualiza campos permitidos
    for campo, valor in dados.items():
        if hasattr(grupo, campo) and valor is not None:
            setattr(grupo, campo, valor)

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


def listar_grupos_por_empresa(
    db: Session,
    *,
    empresa_id: int,
    usuario_id: int,
    plano_trabalho_id: int | None = None,
):
    if not _usuario_pertence_empresa(db, usuario_id, empresa_id):
        raise HTTPException(
            status_code=403,
            detail="Usuário não pertence à empresa",
        )

    if plano_trabalho_id:
        grupos = db.query(Grupos).filter(
            Grupos.plano_id == plano_trabalho_id
        ).all()
    else:
        grupos = (
            db.query(Grupos)
            .filter(
                Grupos.empresa_id == empresa_id,
            )
            .order_by(Grupos.nome)
            .all()
        )

    return grupos

def _usuario_pertence_empresa(db: Session, usuario_id: int, empresa_id: int) -> bool:
    return (
        db.query(EmpresaMembros)
        .filter(
            EmpresaMembros.usuario_id == usuario_id,
            EmpresaMembros.empresa_id == empresa_id,
        )
        .first()
        is not None
    )