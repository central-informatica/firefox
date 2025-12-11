from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.schemas.empresa_convites import (
    EmpresaConviteCreate,
    EmpresaConviteUpdate,
    EmpresaConviteOut
)
from backend.app.crud.empresa_convites import crud_empresa_convites

router = APIRouter(prefix="/empresa-convites", tags=["Empresa Convites"])


@router.get("/", response_model=list[EmpresaConviteOut])
def listar_convites(db: Session = Depends(get_db)):
    return crud_empresa_convites.listar(db)


@router.get("/{convite_id}", response_model=EmpresaConviteOut)
def get_convite(convite_id: int, db: Session = Depends(get_db)):
    return crud_empresa_convites.get(db, convite_id)


@router.post("/", response_model=EmpresaConviteOut)
def criar_convite(data: EmpresaConviteCreate, db: Session = Depends(get_db)):
    return crud_empresa_convites.criar(db, data)


@router.put("/{convite_id}", response_model=EmpresaConviteOut)
def atualizar_convite(convite_id: int, data: EmpresaConviteUpdate, db: Session = Depends(get_db)):
    return crud_empresa_convites.atualizar(db, convite_id, data)


@router.delete("/{convite_id}")
def deletar_convite(convite_id: int, db: Session = Depends(get_db)):
    return crud_empresa_convites.deletar(db, convite_id)
