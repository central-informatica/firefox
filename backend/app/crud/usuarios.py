from sqlalchemy import or_
from sqlalchemy.orm import Session
from backend.app.db.models import Usuarios, Empresas, EmpresaMembros
from backend.app.db.permissions import usuario_pode_gerenciar


from typing import Optional

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

def listar_usuarios_empresa_paginado(
    db: Session,
    empresa_id: int,
    page: int,
    limit: int,
    search: str,
    sort: str,
):
    print("empresa_id: ", empresa_id, page, limit, search, sort)
    query = (
        db.query(Usuarios)
        .join(EmpresaMembros, EmpresaMembros.usuario_id == Usuarios.usuario_id)
        .filter(EmpresaMembros.empresa_id == empresa_id)
    )

    if search:
        like = f"%{search}%"
        query = query.filter(
            or_(
                Usuarios.nome.ilike(like),
                Usuarios.email.ilike(like),
            )
        )

    # sort simples (opcional)
    if sort == "nome":
        query = query.order_by(Usuarios.nome.asc())
    elif sort == "-nome":
        query = query.order_by(Usuarios.nome.desc())
    else:
        query = query.order_by(Usuarios.usuario_id.desc())

    data = (
        query
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    total = query.count()
    tot_adm = len([ad for ad in query if ad.nivel == 'ADMINISTRADOR'])

    return {
        "data": data,
        "total": total,
        "total_adm": tot_adm
    }

def criar_usuario(db: Session, usuario: dict):
    
    novo = Usuarios(**usuario)
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo


def atualizar_usuario(db: Session, empresa_id: Optional[int], usuario_id: int, dados: dict, usuario_logado: Usuarios,):
    usuario = get_usuario(db, usuario_id)
    if not usuario:
        return None
    
    usuario_pode_gerenciar(db, usuario_logado, empresa_id) # Levanta exceção se não tiver permissões
    for key, value in dados.items():
        setattr(usuario, key, value)

    db.commit()
    db.refresh(usuario)
    return usuario


def deletar_usuario(
    db: Session,
    empresa_id: Optional[int],
    usuario_id: int,
    usuario_logado: Usuarios,
):
    usuario = get_usuario(db, usuario_id)
    if not usuario:
        return False

    usuario_pode_gerenciar(db, usuario_logado, empresa_id)

    db.delete(usuario)
    db.commit()
    return True
