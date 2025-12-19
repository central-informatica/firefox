from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.schemas.empresa_membros import (
    EmpresaMembroCreate, EmpresaMembroUpdate, EmpresaMembroOut
)
from backend.app.crud.empresa_membros import crud_empresa_membros

router = APIRouter(prefix="/empresa-membros", tags=["Empresa Membros"])


@router.get("/{membro_id}", response_model=EmpresaMembroOut)
def get_membro(membro_id: int, db: Session = Depends(get_db)):
    return crud_empresa_membros.get(db, membro_id)


@router.get("/empresa/{empresa_id}", response_model=list[EmpresaMembroOut])
def get_membros_empresa(empresa_id: int, db: Session = Depends(get_db)):
    return crud_empresa_membros.get_by_empresa(db, empresa_id)


@router.post("/", response_model=EmpresaMembroOut)
def create_membro(data: EmpresaMembroCreate, db: Session = Depends(get_db)):
    return crud_empresa_membros.create(db, data)


@router.put("/{membro_id}", response_model=EmpresaMembroOut)
def update_membro(membro_id: int, data: EmpresaMembroUpdate, db: Session = Depends(get_db)):
    return crud_empresa_membros.update(db, membro_id, data)


@router.delete("/{membro_id}")
def delete_membro(membro_id: int, db: Session = Depends(get_db)):
    return crud_empresa_membros.delete(db, membro_id)
