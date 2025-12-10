# backend/app/api/crud/empresas.py
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc
from typing import Optional

from backend.app.db.models import Empresas, EmpresaMembros


def crud_listar_empresas_paginado(db: Session, usuario, page: int, limit: int, search: str, sort: str):
    query = (
        db.query(Empresas)
        .join(EmpresaMembros, EmpresaMembros.empresa_id == Empresas.id)
        .filter(EmpresaMembros.usuario_id == usuario.id)
    )

    # search
    if search:
        termo = f"%{search}%"
        query = query.filter(Empresas.razao_social.ilike(termo))

    total = query.count()

    # sort
    if sort:
        if sort.startswith("-"):
            query = query.order_by(desc(sort[1:]))
        else:
            query = query.order_by(asc(sort))

    offset = (page - 1) * limit

    empresas = query.offset(offset).limit(limit).all()

    return {
        "data": [
            {
                "id": e.id,
                "razao_social": e.razao_social,
                "cnpj": e.cnpj,
                "email": e.email,
                "telefone": e.telefone,
                "fuso_horario": e.fuso_horario,
            }
            for e in empresas
        ],
        "total": total,
        "page": page,
        "limit": limit,
    }


def crud_criar_empresa(db: Session, usuario, razao_social, cnpj, email, telefone, fuso_horario):
    nova = Empresas(
        razao_social=razao_social,
        cnpj=cnpj,
        email=email,
        telefone=telefone,
        fuso_horario=fuso_horario,
    )

    db.add(nova)
    db.commit()
    db.refresh(nova)

    vinculo = EmpresaMembros(usuario_id=usuario.id, empresa_id=nova.id)
    db.add(vinculo)
    db.commit()

    return {"message": "Empresa criada com sucesso", "id": nova.id}


def crud_obter_empresa(db: Session, usuario, empresa_id: int):
    return (
        db.query(Empresas)
        .join(EmpresaMembros, EmpresaMembros.empresa_id == Empresas.id)
        .filter(EmpresaMembros.usuario_id == usuario.id)
        .filter(Empresas.id == empresa_id)
        .first()
    )


def crud_atualizar_empresa(
    db: Session,
    usuario,
    empresa_id: int,
    razao_social: str,
    cnpj: str,
    email: str,
    telefone: str,
    fuso_horario: str,
):
    empresa = crud_obter_empresa(db, usuario, empresa_id)

    if not empresa:
        return {"error": "Empresa não encontrada"}

    empresa.razao_social = razao_social
    empresa.cnpj = cnpj
    empresa.email = email
    empresa.telefone = telefone
    empresa.fuso_horario = fuso_horario

    db.commit()
    db.refresh(empresa)

    return {"message": "Empresa atualizada com sucesso"}


def crud_excluir_empresa(db: Session, usuario, empresa_id: int):
    empresa = crud_obter_empresa(db, usuario, empresa_id)

    if not empresa:
        return {"error": "Empresa não encontrada"}

    db.delete(empresa)
    db.commit()

    return {"message": "Empresa excluída com sucesso"}
