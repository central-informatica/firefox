    # backend/app/api/routes/empresas.py

from fastapi import APIRouter, Depends, HTTPException, UploadFile, Form
from sqlalchemy.orm import Session
from typing import Optional

from backend.app.db.database import get_db
from backend.app.db.models import Empresas, EmpresaMembros
#from backend.app.core.security import get_current_user
from backend.app.core.security import validar_token

router = APIRouter(prefix="/empresas", tags=["Empresas"])


# -----------------------------------------------------------
# LISTAGEM PAGINADA
# -----------------------------------------------------------
@router.get("/paginado")
def listar_empresas_paginado(
    page: int = 1,
    limit: int = 10,
    search: Optional[str] = "",
    sort: Optional[str] = "",
    usuario=Depends(validar_token),
    db: Session = Depends(get_db),
):
    query = (
        db.query(Empresas)
        .join(EmpresaMembros, EmpresaMembros.empresa_id == Empresas.id)
        .filter(EmpresaMembros.usuario_id == usuario.id)
    )

    # FILTRO
    if search:
        termo = f"%{search}%"
        query = query.filter(Empresas.razao_social.ilike(termo))

    total = query.count()

    # ORDENAÇÃO
    if sort:
        if sort.startswith("-"):
            campo = sort[1:]
            query = query.order_by(getattr(Empresas, campo).desc())
        else:
            query = query.order_by(getattr(Empresas, sort).asc())

    # PAGINAÇÃO
    offset = (page - 1) * limit
    empresas = query.offset(offset).limit(limit).all()

    # RETORNO PADRÃO DO FRONT
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


# -----------------------------------------------------------
# CRIAR EMPRESA
# -----------------------------------------------------------
@router.post("/")
def criar_empresa(
    razao_social: str = Form(...),
    cnpj: str = Form(...),
    email: str = Form(""),
    telefone: str = Form(""),
    fuso_horario: str = Form(...),
    usuario=Depends(validar_token),
    db: Session = Depends(get_db),
):

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

    # vincular empresa ao usuário
    vinculo = EmpresaMembros(usuario_id=usuario.id, empresa_id=nova.id)
    db.add(vinculo)
    db.commit()

    return {"message": "Empresa criada com sucesso", "id": nova.id}


# -----------------------------------------------------------
# OBTER EMPRESA POR ID
# -----------------------------------------------------------
@router.get("/{empresa_id}")
def obter_empresa(
    empresa_id: int,
    usuario=Depends(validar_token),
    db: Session = Depends(get_db),
):
    empresa = (
        db.query(Empresas)
        .join(EmpresaMembros, EmpresaMembros.empresa_id == Empresas.id)
        .filter(EmpresaMembros.usuario_id == usuario.id)
        .filter(Empresas.id == empresa_id)
        .first()
    )

    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")

    return empresa


# -----------------------------------------------------------
# ATUALIZAR EMPRESA
# -----------------------------------------------------------
@router.put("/{empresa_id}")
def atualizar_empresa(
    empresa_id: int,
    razao_social: str = Form(...),
    cnpj: str = Form(...),
    email: str = Form(""),
    telefone: str = Form(""),
    fuso_horario: str = Form(...),
    usuario=Depends(validar_token),
    db: Session = Depends(get_db),
):

    empresa = (
        db.query(Empresas)
        .join(EmpresaMembros, EmpresaMembros.empresa_id == Empresas.id)
        .filter(EmpresaMembros.usuario_id == usuario.id)
        .filter(Empresas.id == empresa_id)
        .first()
    )

    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")

    empresa.razao_social = razao_social
    empresa.cnpj = cnpj
    empresa.email = email
    empresa.telefone = telefone
    empresa.fuso_horario = fuso_horario

    db.commit()
    db.refresh(empresa)

    return {"message": "Empresa atualizada com sucesso"}


# -----------------------------------------------------------
# EXCLUIR EMPRESA
# -----------------------------------------------------------
@router.delete("/{empresa_id}")
def excluir_empresa(
    empresa_id: int,
    usuario=Depends(validar_token),
    db: Session = Depends(get_db),
):
    empresa = (
        db.query(Empresas)
        .join(EmpresaMembros, EmpresaMembros.empresa_id == Empresas.id)
        .filter(EmpresaMembros.usuario_id == usuario.id)
        .filter(Empresas.id == empresa_id)
        .first()
    )

    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")

    db.delete(empresa)
    db.commit()

    return {"message": "Empresa excluída com sucesso"}
