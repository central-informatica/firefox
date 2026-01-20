from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.schemas.planos_trabalho import (
    PlanoTrabalhoCreate,
    PlanoTrabalhoUpdate,
    PlanoTrabalhoOut,
)
from backend.app.crud.planos_trabalho import crud_planos_trabalho


router = APIRouter(prefix="/planos-trabalho", tags=["Planos de Trabalho"])


@router.get("/", response_model=list[PlanoTrabalhoOut])
def listar(db: Session = Depends(get_db)):
    return crud_planos_trabalho.listar(db)


@router.get("/{plano_id}", response_model=PlanoTrabalhoOut)
def obter(plano_id: int, db: Session = Depends(get_db)):
    return crud_planos_trabalho.get(db, plano_id)


@router.post("/", response_model=PlanoTrabalhoOut, status_code=201)
def criar(data: PlanoTrabalhoCreate, db: Session = Depends(get_db)):
    return crud_planos_trabalho.criar(db, data)


@router.put("/{plano_id}", response_model=PlanoTrabalhoOut)
def atualizar(plano_id: int, data: PlanoTrabalhoUpdate, db: Session = Depends(get_db)):
    return crud_planos_trabalho.atualizar(db, plano_id, data)


@router.delete("/{plano_id}")
def deletar(plano_id: int, db: Session = Depends(get_db)):
    return crud_planos_trabalho.deletar(db, plano_id)
