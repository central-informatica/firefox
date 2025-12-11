from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.schemas.empresas import (
    EmpresaCreate, EmpresaUpdate, EmpresaOut
)
from backend.app.crud.empresas import crud_empresas

router = APIRouter(prefix="/empresas", tags=["Empresas"])


@router.get("/", response_model=list[EmpresaOut])
def listar_empresas(db: Session = Depends(get_db)):
    return crud_empresas.listar(db)


@router.get("/{empresa_id}", response_model=EmpresaOut)
def get_empresa(empresa_id: int, db: Session = Depends(get_db)):
    return crud_empresas.get(db, empresa_id)


@router.post("/", response_model=EmpresaOut)
def criar_empresa(data: EmpresaCreate, db: Session = Depends(get_db)):
    return crud_empresas.criar(db, data)


@router.put("/{empresa_id}", response_model=EmpresaOut)
def atualizar_empresa(empresa_id: int, data: EmpresaUpdate, db: Session = Depends(get_db)):
    return crud_empresas.atualizar(db, empresa_id, data)


@router.delete("/{empresa_id}")
def deletar_empresa(empresa_id: int, db: Session = Depends(get_db)):
    return crud_empresas.deletar(db, empresa_id)
