# backend/app/api/routes/empresas.py
from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from typing import Optional

from backend.app.db.database import get_db
from backend.app.core.security import validar_token
from backend.app.crud.empresas import (
    crud_listar_empresas_paginado,
    crud_criar_empresa,
    crud_obter_empresa,
    crud_atualizar_empresa,
    crud_excluir_empresa,
)

router = APIRouter(prefix="/empresas", tags=["Empresas"])


@router.get("/paginado")
def listar_empresas_paginado(
    page: int = 1,
    limit: int = 10,
    search: Optional[str] = "",
    sort: Optional[str] = "",
    usuario=Depends(validar_token),
    db: Session = Depends(get_db),
):
    return crud_listar_empresas_paginado(db, usuario, page, limit, search, sort)


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
    return crud_criar_empresa(db, usuario, razao_social, cnpj, email, telefone, fuso_horario)


@router.get("/{empresa_id}")
def obter_empresa(
    empresa_id: int,
    usuario=Depends(validar_token),
    db: Session = Depends(get_db),
):
    empresa = crud_obter_empresa(db, usuario, empresa_id)
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")
    return empresa


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
    return crud_atualizar_empresa(
        db, usuario, empresa_id, razao_social, cnpj, email, telefone, fuso_horario
    )


@router.delete("/{empresa_id}")
def excluir_empresa(
    empresa_id: int,
    usuario=Depends(validar_token),
    db: Session = Depends(get_db),
):
    return crud_excluir_empresa(db, usuario, empresa_id)
